import asyncio
import logging
from uuid import UUID

from context import ctx

from shared.logger import configure_logging

logger = logging.getLogger("app")


def process_image(uuid: UUID):
    pass


def process_images():
    pass


async def main():
    configure_logging()
    await ctx.init_db()
    ctx.init_scheduler(process_images)

    ctx.scheduler.start()
    try:
        await asyncio.Future()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        ctx.scheduler.shutdown()
        await ctx.dispose_db()


if __name__ == "__main__":
    asyncio.run(main())
