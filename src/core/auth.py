import logging
import base64
from typing import Annotated, Optional
from binascii import Error as BinasciiError

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from core import models
from core.crud import api_user_get_by_name, api_user_increment_uses
from core.postgres import get_db


class ApiKey:
    def __init__(self, key: str, db: Session) -> None:
        self.unauthenticated = HTTPException(
            status_code=403, detail="Not authenticated"
        )
        self.internal = HTTPException(status_code=500, detail="Internal server error")
        self.logger = logging.getLogger(__name__)

        try:
            prefix, secret = key.split(".")
        except ValueError:
            raise self.unauthenticated
        try:
            self.subject = base64.urlsafe_b64decode(prefix).decode("utf-8")
        except BinasciiError:
            raise self.unauthenticated
        self.secret = secret
        self.db_session = db
        self.api_user: Optional[models.ApiUser]
        self.password_hasher = PasswordHasher()

    async def _get_user(self) -> Optional[models.ApiUser]:
        try:
            return await api_user_get_by_name(
                db=self.db_session, api_user_name=self.subject
            )
        except NoResultFound:
            return None

    def _secrets_equal(self, api_user: models.ApiUser) -> bool:
        try:
            self.password_hasher.verify(hash=api_user.secret, password=self.secret)
        except VerifyMismatchError:
            return False
        else:
            return True

    async def perform_api_use(self) -> None:
        api_user = await self._get_user()
        if not api_user or not self._secrets_equal(api_user=api_user):
            raise self.unauthenticated
        try:
            await api_user_increment_uses(db=self.db_session, api_user=api_user)
        except IntegrityError as e:
            self.logger.error(e)
            raise self.internal


async def authenticate(
    raw_key: Annotated[str, Depends(APIKeyHeader(name="X-API-Key"))],
    db: Session = Depends(get_db),
):
    key = ApiKey(key=raw_key, db=db)
    await key.perform_api_use()


api_key = Depends(authenticate)
