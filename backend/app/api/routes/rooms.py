from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models import Room
from app.schemas.room import INT32_MAX, RoomRead

router = APIRouter(prefix="/rooms", tags=["rooms"])

RoomId = Annotated[int, Path(ge=1, le=INT32_MAX)]
MinCapacity = Annotated[int | None, Query(ge=1, le=INT32_MAX)]


async def get_room_or_404(db: AsyncSession, room_id: int) -> Room:
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.get("", response_model=list[RoomRead])
async def list_rooms(db: DbSession, min_capacity: MinCapacity = None) -> list[Room]:
    query = select(Room).where(Room.is_active).order_by(Room.name)
    if min_capacity is not None:
        query = query.where(Room.capacity >= min_capacity)
    return list(await db.scalars(query))


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: RoomId, db: DbSession) -> Room:
    return await get_room_or_404(db, room_id)
