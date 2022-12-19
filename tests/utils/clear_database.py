from cinemabot.database.base import metadata


EXCLUDED_TABLES = ['alembic_version']


async def clear_database(db) -> None:
    """
    Truncate all tables after tests
    """
    async with db.get_master_session() as session:
        for table in metadata.sorted_tables:
            if table.name in EXCLUDED_TABLES:
                continue
            await session.execute(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;')
