from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.auth import hash_password
from app.db.postgres import async_session
from app.models.user import User

class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, email: str, password: str, full_name: str | None = None) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        async with async_session() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            return result.scalars().first()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def update_last_active(session: AsyncSession, user: User) -> None:
        user.last_active = datetime.utcnow()
        session.add(user)
        await session.commit()
