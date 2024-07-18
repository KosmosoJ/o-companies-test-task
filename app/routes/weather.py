from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
import json 
from cachetools import TTLCache



templates = Jinja2Templates(directory="templates")
router = APIRouter()
cache = TTLCache(maxsize=100, ttl=300)

async def get_cities_info():
    with open('database/cities_info.json', encoding='utf-8') as file:
        data = json.load(file)
    cities_data = []
    for key in data['city']:
        cities_data.append(key['name']) 
    cache['cities'] = cities_data
    return cities_data


@router.get("/weather/")
async def weather_index(request: Request):
    if 'cities' in cache:
        cities_data = cache['cities']
    else:
        cities_data = await get_cities_info()
    print(request.client.host)
    return templates.TemplateResponse(request=request, name="weather.html", context={'cities':cities_data})
