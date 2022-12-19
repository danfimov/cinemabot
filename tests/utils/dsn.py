from cinemabot.config import get_settings


def postgres_dsn() -> str:
    settings = get_settings()
    return (
        f'postgresql://{settings.DB_USER}:'
        f'{settings.DB_PASSWORD}@'
        f'{settings.DB_PATH}:'
        f'{settings.DB_PORT}/'
        f'{settings.DB_NAME}'
    )
