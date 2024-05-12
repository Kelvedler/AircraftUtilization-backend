from sqlalchemy.orm import Session

from core import models


async def get_by_name(db: Session, api_user_name: str) -> models.ApiUser:
    condition = models.ApiUser.name == api_user_name
    return db.query(models.ApiUser).where(condition).one()


async def increment_uses(db: Session, api_user: models.ApiUser) -> None:
    condition = models.ApiUser.id == api_user.id
    db.query(models.ApiUser).where(condition).update(
        {models.ApiUser.uses: models.ApiUser.uses + 1}
    )
    db.commit()
