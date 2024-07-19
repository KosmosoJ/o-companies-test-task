from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
import json
from cachetools import TTLCache
from utils.weather import get_prediction
from database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession


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


@router.get("/weather/")
async def weather_index(request: Request, session: AsyncSession = Depends(get_session)):
    if "cities" in cache:
        cities_data = cache["cities"]
    else:
        cities_data = await get_cities_info()
    return templates.TemplateResponse(
        request=request, name="weather.html", context={"cities": cities_data}
    )


@router.post("/weather/{city_name}")
async def post_weather(city_name: str, session: AsyncSession = Depends(get_session)):
    prediction = await get_prediction(city_name)

    return {
        "prediction": prediction,
    }
