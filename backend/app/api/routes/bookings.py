from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.models import Booking, BookingStatus, Room, UserRole
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.room import INT32_MAX

router = APIRouter(prefix="/bookings", tags=["bookings"])

BookingId = Annotated[int, Path(ge=1, le=INT32_MAX)]

# Postgres error code for a violated EXCLUDE constraint
EXCLUSION_VIOLATION = "23P01"


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate, user: CurrentUser, db: DbSession
) -> Booking:
    room = await db.get(Room, data.room_id)
    if room is None or not room.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")

    booking = Booking(**data.model_dump(), user_id=user.id)
    db.add(booking)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if getattr(exc.orig, "sqlstate", None) == EXCLUSION_VIOLATION:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Room already booked for this time"
            ) from exc
        raise
    await db.refresh(booking)
    return booking


@router.get("/me", response_model=list[BookingRead])
async def my_bookings(
    user: CurrentUser, db: DbSession, upcoming: bool = False
) -> list[Booking]:
    query = select(Booking).where(Booking.user_id == user.id)
    if upcoming:
        query = query.where(
            Booking.status == BookingStatus.ACTIVE, Booking.ends_at > func.now()
        )
    return list(await db.scalars(query.order_by(Booking.starts_at)))


@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: BookingId, user: CurrentUser, db: DbSession
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    if booking.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your booking")
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Booking already cancelled")

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    return booking
