import logging
from typing import Annotated
from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter

from core import crud, http_errors, schemas
from core.mongodb import MongodbConn

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/operators/",
    response_model=list[schemas.OperatorMetric],
    responses={
        403: http_errors.HTTPUnauthorized.EXAMPLE,
        500: http_errors.HTTPInternal.EXAMPLE,
    },
)
async def get_metrics_for_operators(
    mongodb: MongodbConn,
    operator: Annotated[
        list[Annotated[str, Query(min_length=3, max_length=50, examples=["operator"])]],
        Query(min_length=1, max_length=10),
    ] = [],
    owner: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
    built_interval: schemas.BuiltInterval = Depends(),
    landed_interval: schemas.LandedInterval = Depends(),
):
    operators_metric = await crud.metrics_operator_get_page(
        operators=operator,
        owner=owner,
        built_interval=built_interval,
        landed_interval=landed_interval,
        db=mongodb,
    )
    return operators_metric
