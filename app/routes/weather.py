from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
import json
from cachetools import TTLCache
from utils.weather import get_prediction
from database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils.city import user_get_city_info, get_cities_info_db
from utils.search import post_user_search, get_unique_user_search, get_user_searches
from schemas.search import UserSearch


templates = Jinja2Templates(directory="templates")
router = APIRouter()
cache = TTLCache(maxsize=100, ttl=300)


async def get_cities_info():
    with open("database/cities_info.json", encoding="utf-8") as file:
        data = json.load(file)
    cities_data = []
    for key in data["city"]:
        cities_data.append(key["name"])
    cache["cities"] = cities_data
    return cities_data


@router.get("/")
async def weather_index(request: Request, session: AsyncSession = Depends(get_session)):
    if "cities" in cache:
        cities_data = cache["cities"]
    else:
        cities_data = await get_cities_info()
    user_searches = await get_unique_user_search(request.client.host, session)
    print(user_searches)
    return templates.TemplateResponse(
        request=request,
        name="weather.html",
        context={"cities": cities_data, "user_search": user_searches},
    )


@router.post("/weather/{city_name}")
async def post_weather(
    city_name: str, request: Request, session: AsyncSession = Depends(get_session)
):
    prediction = await get_prediction(city_name)
    if prediction:
        await user_get_city_info(city_name, session)
        user = UserSearch(user_host=request.client.host, user_request=city_name)
        await post_user_search(user, session)
    return {
        "prediction": prediction,
    }


@router.get("/admin")
async def admin_weather(request: Request, session: AsyncSession = Depends(get_session)):
    context = {}
    cities = await get_cities_info_db(session)
    users = await get_user_searches(session)

    context.update({"cities": cities, "users": users})

    return templates.TemplateResponse(
        request=request, name="admin_weather.html", context=context
    )


@router.get("/admin/cities")
async def admin_cities_info(session: AsyncSession = Depends(get_session)):
    cities = await get_cities_info_db(session)
    return [{"City name": c.city_name, "Searched times": c.searched} for c in cities]


@router.get("/admin/users")
async def admin_users_info(session: AsyncSession = Depends(get_session)):
    users = await get_user_searches(session)
    return [
        {"Client": u.user_host, "Request": u.user_request, "Searched at": u.searched_at}
        for u in users
    ]
