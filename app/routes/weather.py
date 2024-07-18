from fastapi import APIRouter, status, Form
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated
import json
from cachetools import TTLCache
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import time


from geopy.geocoders import Nominatim


templates = Jinja2Templates(directory="templates")
router = APIRouter()
cache = TTLCache(maxsize=100, ttl=300)
geolocator = Nominatim(user_agent="weather_app")
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


async def request_openmeteo(location: dict):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": [
            "temperature_2m",
            "is_day",
            "rain",
            "snowfall",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m"],
        "past_days": 2,
        "forecast_days": 8,
    }
    responses = openmeteo.weather_api(url=url, params=params)
    return responses[0]


async def get_cities_info():
    with open("database/cities_info.json", encoding="utf-8") as file:
        data = json.load(file)
    cities_data = []
    for key in data["city"]:
        cities_data.append(key["name"])
    cache["cities"] = cities_data
    return cities_data


@router.get("/weather/")
async def weather_index(request: Request):
    if "cities" in cache:
        cities_data = cache["cities"]
    else:
        cities_data = await get_cities_info()
    return templates.TemplateResponse(
        request=request, name="weather.html", context={"cities": cities_data}
    )


@router.post("/weather/")
async def post_weather(city_name: Annotated[str, Form()], request: Request):
    location = geolocator.geocode(city_name)

    info = await request_openmeteo(
        {"latitude": location.latitude, "longitude": location.longitude}
    )
    hourly = info.Hourly()

    # Получение дат
    raw_dates = [hourly.Time()]
    a = hourly.Time()
    while a != hourly.TimeEnd():
        a += hourly.Interval()
        raw_dates.append(a)
    dates = [
        datetime.fromtimestamp(date).strftime("%d-%m-%Y %H:%M:%S") for date in raw_dates
    ]
    temperatures = hourly.Variables(0).ValuesAsNumpy().tolist()
    precipitation_chance = hourly.Variables(1).ValuesAsNumpy().tolist()
    wind = hourly.Variables(2).ValuesAsNumpy().tolist()

    prediction = {}
    a = 0
    for index, date in enumerate(dates[19:-6]):
        if a == 5:
            prediction[date] = {
                "temp": temperatures[index],
                "precip_chance": precipitation_chance[index],
                "wind": wind[index],
            }
            a = 0
        else:
            a += 1

    # prediction = dict(zip(dates, hourly.Variables(0).ValuesAsNumpy().tolist()))

    return {
        "current_temp": info.Current().Variables(0).Value(),
        "prediction": prediction,
    }
    return RedirectResponse("/weather/", status_code=status.HTTP_303_SEE_OTHER)
