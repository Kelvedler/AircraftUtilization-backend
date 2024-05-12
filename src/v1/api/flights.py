from typing import Annotated, List, Union

from fastapi import APIRouter, Query
from fastapi.param_functions import Depends

from core import crud, schemas
from core.mongodb import MongodbConn

router = APIRouter()


@router.get("/", response_model=List[schemas.Flights])
async def get_flights(
    mongodb: MongodbConn,
    page: Annotated[int, Query(ge=1, le=1000)] = 1,
    icao24: Annotated[Union[str, None], Query(min_length=6, max_length=6)] = None,
    landed_interval: schemas.LandedInterval = Depends(),
    duration_interval: schemas.DurationInterval = Depends(),
):
    flights = await crud.flights_get_page(
        page=page,
        icao24=icao24,
        landed_interval=landed_interval,
        duration_interval=duration_interval,
        db=mongodb,
    )
    return flights
