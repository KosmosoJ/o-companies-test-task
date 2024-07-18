from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/weather/")
async def weather_index(request: Request):
    print(request.client.host)
    return templates.TemplateResponse(request=request, name="weather.html")
