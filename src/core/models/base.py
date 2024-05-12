from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID
from datetime import datetime


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
