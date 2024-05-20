from decimal import Decimal
from pydantic import PositiveInt
from pydantic.fields import Field
from pydantic.main import BaseModel


class OperatorMetric(BaseModel):
    operator: str = Field(min_length=3, max_length=50, examples=["Dream Air"])
    fleet_size: PositiveInt = Field(examples=[10])
    models: list[str] = Field(examples=[["B737", "B737 NG"]])
    flights_recorded: PositiveInt = Field(examples=[10])
    flight_duration_avg: Decimal = Field(examples=[72.4])
