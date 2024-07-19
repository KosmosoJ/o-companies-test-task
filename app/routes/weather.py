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
    """ Подтягивание городов из json файла, для отображения подсказки в input """
    with open("database/cities_info.json", encoding="utf-8") as file:
        data = json.load(file)
    cities_data = []
    for key in data["city"]:
        cities_data.append(key["name"])
    cache["cities"] = cities_data
    return cities_data


@router.get("/")
async def weather_index(request: Request, session: AsyncSession = Depends(get_session)):
    """ Роут для поиска прогноза погоды """
    if "cities" in cache:
        cities_data = cache["cities"]
    else:
        cities_data = await get_cities_info()
    user_searches = await get_unique_user_search(request.client.host, session)
    return templates.TemplateResponse(
        request=request,
        name="weather.html",
        context={"cities": cities_data, "user_search": user_searches},
    )


@router.post("/weather/{city_name}")
async def post_weather(
    
    city_name: str, request: Request, session: AsyncSession = Depends(get_session)
):
    """ Пост запрос для получения прогноза погоды """
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
    """ Небольшая реализация 'админ' панели, для более удобного просмотра информации из бд """
    context = {}
    try:
        cities = await get_cities_info_db(session)
        users = await get_user_searches(session)
        
    except:
        cities = None
        users = None 
        
    context['cities'] = cities
    context['users'] = users 
    

    return templates.TemplateResponse(
        request=request, name="admin_weather.html", context=context
    )


@router.get("/admin/cities")
async def admin_cities_info(session: AsyncSession = Depends(get_session)):
    """ Апи для получения информации по всем городам /admin/cities """
    cities = await get_cities_info_db(session)
    return [{"City name": c.city_name, "Searched times": c.searched} for c in cities]


@router.get("/admin/users")
async def admin_users_info(session: AsyncSession = Depends(get_session)):
    """ Апи для получения информации о всех пользователях, которые пользовались поиском /admin/users """
    users = await get_user_searches(session)
    return [
        {"Client": u.user_host, "Request": u.user_request, "Searched at": u.searched_at}
        for u in users
    ]
