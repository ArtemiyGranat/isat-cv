import logging
from typing import ClassVar, List, Optional, Type

from databases import Database
from pydantic import BaseModel, TypeAdapter

from shared.resources import DatabaseCredentials

logger = logging.getLogger("app")


class Entity(BaseModel):
    _table_name: ClassVar[str]
    _pk: ClassVar[str]


class AbstractRepository:
    def __init__(self, db: Database, entity: Type[Entity]):
        self._db = db
        self._entity = entity
        self._table_name = entity._table_name

    def _get_query_parameters(self, dump):
        keys = list(dump.keys())
        columns = ",".join(keys)
        placeholders = ",".join(map(lambda x: f":{x}", keys))
        return columns, placeholders

    async def add(
        self, entities: BaseModel | List[BaseModel], ignore_conflict=False
    ):
        if not isinstance(entities, list):
            entities = [entities]

        if not entities:
            return

        dumps = [entity.model_dump() for entity in entities]
        columns, placeholders = self._get_query_parameters(dumps[0])

        query = f"INSERT INTO {self._table_name}({columns}) VALUES ({placeholders})"

        if ignore_conflict:
            query += " ON CONFLICT DO NOTHING"

        await self._db.execute_many(query=query, values=dumps)
        logger.debug(f"Sent query: {query}")

    async def get_one(self, field, value) -> Optional[Entity]:
        query = f"SELECT * FROM {self._table_name}"
        query += f" WHERE {field} = :{field}"
        row = await self._db.fetch_one(query=query, values={field: value})
        logger.debug(f"Sent query: {query}")

        if not row:
            return None

        return TypeAdapter(self._entity).validate_python(dict(row._mapping))

    async def get_many(self, field=None, value=None) -> List[Entity]:
        query = f"SELECT * FROM {self._table_name}"
        if field is not None:
            query += f" WHERE {field} = :{field}"
            rows = await self._db.fetch_all(query=query, values={field: value})
        else:
            rows = await self._db.fetch_all(query=query)
        logger.debug(f"Sent query: {query}")

        mapped = map(
            lambda row: TypeAdapter(self._entity).validate_python(
                dict(row._mapping)
            ),
            rows,
        )

        return list(mapped)


class SqliteRepository(AbstractRepository):
    async def create_table(self):
        await self._db.execute(
            query=f"CREATE TABLE IF NOT EXISTS {self._table_name} (id TEXT, path TEXT, hash TEXT);"
        )


def gen_sqlite_address(creds: DatabaseCredentials):
    return f"{creds.driver}:///{creds.db_name}.db"
