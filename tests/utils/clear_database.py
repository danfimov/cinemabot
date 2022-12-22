from cinemabot.database.base import metadata
from cinemabot.database.connector import DatabaseConnector


EXCLUDED_TABLES = ['alembic_version']


async def clear_database(db: DatabaseConnector) -> None:
    """
    Truncate all tables after tests
    """
    async with db.get_master_session() as session:
        for table in metadata.sorted_tables:
            if table.name in EXCLUDED_TABLES:
                continue
            await session.execute(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;')
