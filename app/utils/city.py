from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import City
from fastapi import HTTPException, status


async def get_cities_info(session: AsyncSession):
    cities = await session.execute(select(City))
    cities = cities.scalars().all()
    if not cities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return cities


async def get_city_info(city: str, session: AsyncSession):
    city_info = await session.execute(
        select(City).where(City.city_name == city.lower())
    )
    city_info = city_info.scalars().first()

    if not city_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return city_info


async def user_get_city_info(city: str, session: AsyncSession):
    city_info = await session.execute(
        select(City).where(City.city_name == city.lower())
    )
    city_info = city_info.scalars().first()
    if not city_info:
        new_city = City(city_name=city.lower(), searched=1)
        session.add(new_city)
        await session.commit()
        return new_city
    city_info.searched += 1
    await session.commit()
    return city_info
