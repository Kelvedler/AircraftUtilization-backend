from sqlalchemy.types import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class ApiUser(BaseModel):
    __tablename__ = "api_user"

    name: Mapped[str] = mapped_column(VARCHAR(length=30))
    secret: Mapped[str] = mapped_column(VARCHAR(length=128))
    uses: Mapped[int]
    active: Mapped[bool] = mapped_column(server_default="1")
