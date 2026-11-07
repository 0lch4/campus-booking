from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models import Room
from app.schemas.room import INT32_MAX, RoomCreate, RoomRead, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])

RoomId = Annotated[int, Path(ge=1, le=INT32_MAX)]
MinCapacity = Annotated[int | None, Query(ge=1, le=INT32_MAX)]


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


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(data: RoomCreate, db: DbSession) -> Room:
    room = Room(**data.model_dump())
    db.add(room)
    await commit_or_409(db)
    return room


@router.patch("/{room_id}", response_model=RoomRead)
async def update_room(room_id: RoomId, data: RoomUpdate, db: DbSession) -> Room:
    room = await get_room_or_404(db, room_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    await commit_or_409(db)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_room(room_id: RoomId, db: DbSession) -> None:
    room = await get_room_or_404(db, room_id)
    room.is_active = False
    await db.commit()
