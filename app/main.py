from fastapi import FastAPI
from routes.weather import router as weather_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()


app.include_router(weather_router)
app.mount('/templates/static', StaticFiles(directory='templates/static'), name='static')


@app.get("/")
async def index():
    return {"message": "app started"}
