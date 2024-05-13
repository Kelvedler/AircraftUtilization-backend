from typing import Annotated, List
from fastapi import APIRouter, Query
from core import crud, http_errors

from core.mongodb import MongodbConn
from core.schemas import Aircraft

router = APIRouter()


@router.get(
    "/",
    response_model=List[Aircraft],
    responses={
        403: http_errors.HTTPUnauthorized.EXAMPLE,
        500: http_errors.HTTPInternal.EXAMPLE,
    },
)
async def get_aircraft(
    mongodb: MongodbConn,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
):
    aircraft = await crud.aircraft_get_page(page=page, db=mongodb)
    return aircraft
