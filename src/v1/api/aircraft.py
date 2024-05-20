from typing import Annotated

from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter

from core import crud, http_errors
from core import schemas
from core.mongodb import MongodbConn

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.AircraftPage,
    responses={
        403: http_errors.HTTPUnauthorized.EXAMPLE,
        500: http_errors.HTTPInternal.EXAMPLE,
    },
)
async def get_aircraft(
    mongodb: MongodbConn,
    page: Annotated[int, Query(ge=1, le=100_000)] = 1,
    model: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    manufacturer: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    owner: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    operator: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    built_interval: schemas.BuiltInterval = Depends(),
):
    aircraft = await crud.aircraft_get_page(
        page=page,
        model=model,
        manufacturer=manufacturer,
        owner=owner,
        operator=operator,
        built_interval=built_interval,
        db=mongodb,
    )
    return aircraft
