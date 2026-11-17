from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Largest value of a Postgres int column
INT32_MAX = 2_147_483_647

ShortText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
Capacity = Annotated[int, Field(gt=0, le=INT32_MAX)]


class RoomCreate(BaseModel):
    name: ShortText
    building: ShortText
    capacity: Capacity
    description: str | None = None


class RoomUpdate(BaseModel):
    # Omitted fields stay unchanged. Only description accepts an explicit null,
    # the other defaults are never validated, so sending null for them is a 422.
    name: ShortText = None
    building: ShortText = None
    capacity: Capacity = None
    description: str | None = None
    is_active: bool = None


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: str
    capacity: int
    description: str | None
    is_active: bool
    created_at: datetime
