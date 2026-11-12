from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, get_current_user, require_admin
from app.models import Booking, BookingStatus, Room
from app.schemas.booking import BookingRead
from app.schemas.room import INT32_MAX, RoomCreate, RoomRead, RoomUpdate

# Reading needs any logged in user, changes need an admin
router = APIRouter(
    prefix="/rooms", tags=["rooms"], dependencies=[Depends(get_current_user)]
)
admin_only = [Depends(require_admin)]

RoomId = Annotated[int, Path(ge=1, le=INT32_MAX)]
MinCapacity = Annotated[int | None, Query(ge=1, le=INT32_MAX)]
RangeFrom = Annotated[datetime, Query(alias="from")]
RangeTo = Annotated[datetime, Query(alias="to")]


async def get_room_or_404(db: AsyncSession, room_id: int) -> Room:
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


async def commit_or_409(db: AsyncSession) -> None:
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Room name already taken"
        ) from exc


@router.get("", response_model=list[RoomRead])
async def list_rooms(db: DbSession, min_capacity: MinCapacity = None) -> list[Room]:
    query = select(Room).where(Room.is_active).order_by(Room.name)
    if min_capacity is not None:
        query = query.where(Room.capacity >= min_capacity)
    return list(await db.scalars(query))


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: RoomId, db: DbSession) -> Room:
    return await get_room_or_404(db, room_id)


@router.get("/{room_id}/bookings", response_model=list[BookingRead])
async def room_bookings(
    room_id: RoomId, range_from: RangeFrom, range_to: RangeTo, db: DbSession
) -> list[Booking]:
    if range_from.tzinfo is None or range_to.tzinfo is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "from and to need a timezone"
        )
    if range_to <= range_from:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "to must be after from"
        )
    await get_room_or_404(db, room_id)
    query = (
        select(Booking)
        .where(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.ACTIVE,
            Booking.starts_at < range_to,
            Booking.ends_at > range_from,
        )
        .order_by(Booking.starts_at)
    )
    return list(await db.scalars(query))


@router.post(
    "",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=admin_only,
)
async def create_room(data: RoomCreate, db: DbSession) -> Room:
    room = Room(**data.model_dump())
    db.add(room)
    await commit_or_409(db)
    return room


@router.patch("/{room_id}", response_model=RoomRead, dependencies=admin_only)
async def update_room(room_id: RoomId, data: RoomUpdate, db: DbSession) -> Room:
    room = await get_room_or_404(db, room_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    await commit_or_409(db)
    return room


@router.delete(
    "/{room_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin_only
)
async def deactivate_room(room_id: RoomId, db: DbSession) -> None:
    room = await get_room_or_404(db, room_id)
    room.is_active = False
    await db.commit()
