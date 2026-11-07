"""Test data for local development. Safe to run more than once."""

import asyncio

from sqlalchemy.dialects.postgresql import insert

from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Room, User, UserRole

USERS = [
    ("admin@example.com", "admin123", "Test Admin", UserRole.ADMIN),
    ("user@example.com", "user123", "Test User", UserRole.USER),
]

ROOMS = [
    {
        "name": "A-101",
        "building": "A",
        "capacity": 30,
        "description": "Lecture room with a projector",
    },
    {
        "name": "A-102",
        "building": "A",
        "capacity": 12,
        "description": "Small meeting room",
    },
    {
        "name": "B-201",
        "building": "B",
        "capacity": 60,
        "description": "Large lecture hall",
    },
    {"name": "B-202", "building": "B", "capacity": 20, "description": None},
]


async def seed() -> None:
    users = [
        {
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "role": role,
        }
        for email, password, full_name, role in USERS
    ]

    async with SessionLocal() as session:
        await session.execute(
            insert(User).values(users).on_conflict_do_nothing(index_elements=["email"])
        )
        await session.execute(
            insert(Room).values(ROOMS).on_conflict_do_nothing(index_elements=["name"])
        )
        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
