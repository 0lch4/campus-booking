from datetime import UTC, datetime
from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from app.models import BookingStatus
from app.schemas.room import INT32_MAX

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


class BookingCreate(BaseModel):
    room_id: Annotated[int, Field(ge=1, le=INT32_MAX)]
    title: Title
    starts_at: AwareDatetime
    ends_at: AwareDatetime

    @model_validator(mode="after")
    def check_times(self) -> Self:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        if self.starts_at < datetime.now(UTC):
            raise ValueError("starts_at can't be in the past")
        return self


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    status: BookingStatus
    created_at: datetime
