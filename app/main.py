from fastapi import FastAPI
from routes.weather import router as weather_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.include_router(weather_router)
app.mount('/templates/static', StaticFiles(directory='templates/static'), name='static')


origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"message": "app started"}
