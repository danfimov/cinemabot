from sqlalchemy import Column, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP

from cinemabot.database.base import DeclarativeBase as Base
from cinemabot.database.mixins import UUIdMixin


class User(Base):  # type: ignore
    __tablename__ = "user"

    id = Column(BIGINT, primary_key=True)


class SearchHistory(Base, UUIdMixin):  # type: ignore
    __tablename__ = "search_history"

    user_id = Column(
        ForeignKey(
            "user.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    request_text = Column(Text)
    dt_created = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
        index=True,
        doc="Date and time of create (type TIMESTAMP)",
    )

    def __repr__(self) -> str:
        return f"<SearchHistory user={self.user_id} text={self.request_text}>"


class Film(Base, UUIdMixin):  # type: ignore
    __tablename__ = "film"

    name_ru = Column(Text)
    name_eng = Column(Text)
    kinopoisk_id = Column(Integer, index=True)


class UserFilmView(Base, UUIdMixin):  # type: ignore
    __tablename__ = "user_film_view"

    user_id = Column(
        ForeignKey(
            "user.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    film_id = Column(
        ForeignKey(
            "film.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    views = Column(
        Integer,
        server_default=text("0"),
    )


__all__ = [
    "User",
    "Film",
    "UserFilmView",
    "SearchHistory",
]
