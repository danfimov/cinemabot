from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID


class UUIdMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        unique=True,
        doc="Unique index of element (type UUID)",
    )
