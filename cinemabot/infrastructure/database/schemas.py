import datetime as dt
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, as_declarative, mapped_column


sa_metadata = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


@as_declarative(metadata=sa_metadata)
class BaseTableSchema:
    created_at: Mapped[dt.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=dt.datetime.now,
        onupdate=dt.datetime.now,
    )


class UUIdMixin:
    id = mapped_column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.func.gen_random_uuid(),
        unique=True,
        doc="Unique index of element (type UUID)",
    )


class User(BaseTableSchema):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(postgresql.BIGINT, primary_key=True)


class SearchHistory(BaseTableSchema, UUIdMixin):
    __tablename__ = "search_history"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey(
            "user.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    request_text: Mapped[str] = mapped_column(postgresql.TEXT)

    def __repr__(self) -> str:
        return f"<SearchHistory user={self.user_id} text={self.request_text}>"


class Film(BaseTableSchema, UUIdMixin):
    __tablename__ = "film"

    name_ru: Mapped[str] = mapped_column(postgresql.TEXT)
    name_eng: Mapped[str] = mapped_column(postgresql.TEXT)
    kinopoisk_id: Mapped[int] = mapped_column(postgresql.INTEGER, index=True)


class UserFilmView(BaseTableSchema, UUIdMixin):
    __tablename__ = "user_film_view"

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey(
            "user.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    film_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey(
            "film.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        index=True,
    )
    views: Mapped[int] = mapped_column(
        postgresql.INTEGER,
        server_default=sa.text("0"),
    )


__all__ = [
    "User",
    "Film",
    "UserFilmView",
    "SearchHistory",
]
