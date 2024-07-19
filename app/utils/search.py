from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import UserSearch
from fastapi import HTTPException, status
from schemas import search as search_schemas


async def get_user_searches(session: AsyncSession):
    """ Получение всех поисков пользователей """
    search_info = await session.execute(select(UserSearch))
    search_info = search_info.scalars().all()

    if not search_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return search_info


async def get_unique_user_search(user_host: str, session: AsyncSession):
    """ Получение последних данных, введенных конкретным пользователем.
      Используется для вывода в "Искали ранее" """
    search_info = await session.execute(
        select(UserSearch)
        .where(UserSearch.user_host == user_host)
        .limit(5)
        .order_by(desc(UserSearch.id))
    )
    search_info = search_info.scalars().all()
    if not search_info:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return search_info


async def get_user_search(user_host: str, session: AsyncSession):
    """ Получение пользователя по айпи (не используется) """
    user_search_info = await session.execute(
        select(UserSearch).where(UserSearch.user_host == user_host)
    )
    user_search_info = user_search_info.scalars().first()

    if not user_search_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user_search_info


async def post_user_search(user_info: search_schemas.UserSearch, session: AsyncSession):
    """ Сохранение в бд информации о поиске клиента """
    new_search = UserSearch(
        user_host=user_info.user_host, user_request=user_info.user_request
    )
    session.add(new_search)
    await session.commit()
    return new_search
