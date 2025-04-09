import abc

from cinemabot.infrastructure.database.schemas import Film, SearchHistory, User, UserFilmView


# TODO: split to separate repositories
class AbstractStorageRepository(abc.ABC):
    @abc.abstractmethod
    async def create_user(
        self,
        user_id: int,
        get_or_create: bool = False,
    ) -> User: ...

    @abc.abstractmethod
    async def get_or_create_film(
        self,
        film_kinopoisk_id: int,
        film_name_ru: str,
        film_name_eng: str,
    ) -> Film: ...

    @abc.abstractmethod
    async def get_or_create_user_film_view(
        self,
        user_id: int,
        film_id: int,
    ) -> UserFilmView: ...

    @abc.abstractmethod
    async def add_request_to_history(
        self,
        user_id: int,
        request_text: str,
    ) -> None: ...

    @abc.abstractmethod
    async def increase_number_of_film_view(
        self,
        user_id: int,
        film_kinopoisk_id: int,
        film_name_ru: str,
        film_name_eng: str,
    ) -> None: ...

    @abc.abstractmethod
    async def get_search_history(
        self,
        user_id: int,
        page_number: int,
        page_size: int = 10,
    ) -> list[SearchHistory]: ...

    async def get_stats(
        self,
        user_id: int,
        page_number: int,
        page_size: int = 10,
    ) -> list[tuple[int, str]]: ...
