"""create_new_entities

Revision ID: d2f92c9402e0
Revises:
Create Date: 2022-12-12 12:18:09.163494

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "d2f92c9402e0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "film",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name_ru", sa.Text(), nullable=True),
        sa.Column("name_eng", sa.Text(), nullable=True),
        sa.Column("kinopoisk_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__film")),
        sa.UniqueConstraint("id", name=op.f("uq__film__id")),
    )
    op.create_index(op.f("ix__film__kinopoisk_id"), "film", ["kinopoisk_id"], unique=False)
    op.create_table("user", sa.Column("id", sa.Integer(), nullable=False), sa.PrimaryKeyConstraint("id", name=op.f("pk__user")))
    op.create_table(
        "search_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("request_text", sa.Text(), nullable=True),
        sa.Column(
            "dt_created",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk__search_history__user_id__user"),
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__search_history")),
        sa.UniqueConstraint("id", name=op.f("uq__search_history__id")),
    )
    op.create_index(op.f("ix__search_history__dt_created"), "search_history", ["dt_created"], unique=False)
    op.create_index(op.f("ix__search_history__user_id"), "search_history", ["user_id"], unique=False)
    op.create_table(
        "user_film_view",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("film_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["film_id"],
            ["film.id"],
            name=op.f("fk__user_film_view__film_id__film"),
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk__user_film_view__user_id__user"),
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__user_film_view")),
        sa.UniqueConstraint("id", name=op.f("uq__user_film_view__id")),
    )
    op.create_index(op.f("ix__user_film_view__film_id"), "user_film_view", ["film_id"], unique=False)
    op.create_index(op.f("ix__user_film_view__user_id"), "user_film_view", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__user_film_view__user_id"), table_name="user_film_view")
    op.drop_index(op.f("ix__user_film_view__film_id"), table_name="user_film_view")
    op.drop_table("user_film_view")
    op.drop_index(op.f("ix__search_history__user_id"), table_name="search_history")
    op.drop_index(op.f("ix__search_history__dt_created"), table_name="search_history")
    op.drop_table("search_history")
    op.drop_table("user")
    op.drop_index(op.f("ix__film__kinopoisk_id"), table_name="film")
    op.drop_table("film")
    # ### end Alembic commands ###
