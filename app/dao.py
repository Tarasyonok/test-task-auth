from app.database import async_session_maker
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import selectinload
from app.models import User, Role, Permission


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(selectinload(User.role).selectinload(Role.permissions))
                .filter_by(**filter_by)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()["id"]

    @classmethod
    async def delete_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(id=model_id)
            await session.execute(query)
            await session.commit()


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def update(cls, user_id: int, **data):
        from app.auth import get_password_hash

        async with async_session_maker() as session:
            if "password" in data:
                data["hashed_password"] = get_password_hash(data.pop("password"))

            query = (
                update(cls.model)
                .where(cls.model.id == user_id)
                .values(**data)
                .returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one()


class RoleDAO(BaseDAO):
    model = Role


class PermissionDAO(BaseDAO):
    model = Permission
