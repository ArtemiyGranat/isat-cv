import logging
from typing import ClassVar, List, Optional, Tuple, Type

import numpy as np
from asyncpg.exceptions import UniqueViolationError
from databases import Database
from pydantic import BaseModel, TypeAdapter

from shared.models import Distance
from shared.resources import DatabaseCredentials

logger = logging.getLogger("app")


class Entity(BaseModel):
    _table_name: ClassVar[str]
    _pk: ClassVar[str]


class AbstractRepository:
    def __init__(self, db: Database, entity: Type[Entity]) -> None:
        self._db = db
        self._entity = entity
        self._table_name = entity._table_name

    def _get_query_parameters(self, dump) -> Tuple[str, str]:
        keys = list(dump.keys())
        columns = ",".join(keys)
        placeholders = ",".join(f":{key}" for key in keys)
        return columns, placeholders

    async def add(
        self, entities: BaseModel | List[BaseModel], ignore_conflict=False
    ) -> None:
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

    async def update(self, entity: Entity, fields: List[str]) -> None:
        dump = entity.model_dump()

        pk = entity._pk
        query_set = ",".join(f"{field} = :{field}" for field in fields)
        query = f"UPDATE {self._table_name} SET {query_set} WHERE {pk} = :{pk}"

        await self._db.execute(
            query=query, values={k: dump[k] for k in fields} | {pk: dump[pk]}
        )
        logger.debug(f"Sent query: {query}")

    async def get_one(self, field, value) -> Optional[Entity]:
        query = f"SELECT * FROM {self._table_name} WHERE {field} = :{field}"

        row = await self._db.fetch_one(query=query, values={field: value})
        logger.debug(f"Sent query: {query}")

        return (
            TypeAdapter(self._entity).validate_python(dict(row._mapping))
            if row
            else None
        )

    async def get_many(self, field=None, value=None) -> List[Entity]:
        query = f"SELECT * FROM {self._table_name}"

        if field is not None:
            query += f" WHERE {field} = :{field}"
            rows = await self._db.fetch_all(query=query, values={field: value})
        else:
            rows = await self._db.fetch_all(query=query)

        logger.debug(f"Sent query: {query}")

        return [
            TypeAdapter(self._entity).validate_python(dict(row._mapping))
            for row in rows
        ]


# TODO: PgVectorRepository?
# TODO: move get_many_from list to AbstractRepository and add select
# specified field support
# TODO: type hints
class PgRepository(AbstractRepository):
    async def add_or_update(self, entity: Entity, fields: List[str]):
        try:
            await self.add(entity)
        except UniqueViolationError:
            await self.update(entity, fields)

    async def get_many_from_list(self, field, values) -> List[Entity]:
        if values is None or not values:
            return []

        placeholders = ", ".join(
            [":value{}".format(i) for i, _ in enumerate(values)]
        )
        query = f"SELECT * FROM {self._table_name}"

        if field is not None:
            query += f" WHERE {field} IN ({placeholders})"
            rows = await self._db.fetch_all(
                query=query,
                values={f"value{i}": v for i, v in enumerate(values)},
            )
        else:
            rows = await self._db.fetch_all(query=query)

        return [
            TypeAdapter(self._entity).validate_python(dict(row._mapping))
            for row in rows
        ]

    async def get_nearest_embeddings(
        self,
        embedding_field,
        embedding,
        distance_type,
        amount,
        field=None,
        value=None,
    ):
        embedding = np.array2string(embedding, separator=", ")
        query = f"SELECT * FROM {self._table_name}"

        if field is not None:
            query += f" WHERE {field} = :{field}"

        distance = {
            Distance.COSINE_SIMILARITY: f"1 - ({embedding_field} <=> '{embedding}') DESC",
            Distance.DISTANCE: f"{embedding_field} <-> '{embedding}'",
            Distance.INNER_PRODUCT: f"({embedding_field} <#> '{embedding}') * -1",
        }

        query += f" ORDER BY {distance[distance_type]} LIMIT {amount}"

        if field is not None:
            rows = await self._db.fetch_all(query=query, values={field: value})
        else:
            rows = await self._db.fetch_all(query=query)

        logger.debug(f"Sent query: {query}")

        return [
            TypeAdapter(self._entity).validate_python(dict(row._mapping))
            for row in rows
        ]


# FIXME: pg_creds and type hint
def gen_db_address(creds: DatabaseCredentials):
    return f"{creds.driver}://{creds.username}:{creds.password}@{creds.url}:{creds.port}/{creds.db_name}"
