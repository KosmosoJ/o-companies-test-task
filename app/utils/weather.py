import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta


from geopy.geocoders import Nominatim

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


async def get_prediction(city_name):
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
    days_segments = {
        0: "morning",  # 6:00
        1: "day",  # 12:00
        2: "evening",  # 18:00
        3: "night",  # 23:00
    }
    a = 0

    for index, date in enumerate(dates[19:-6]):
        date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
        if date.hour in [6, 12, 18, 23]:
            if a == 4:
                a = 0
            if (
                (
                    datetime.now()
                    - timedelta(
                        days=1, minutes=datetime.now().minute, hours=datetime.now().hour
                    )
                )
                < date
                < (datetime.now() + timedelta(days=7, hours=23 - datetime.now().hour))
            ):
                try:
                    if prediction[f"{date.day}.{date.month}"]:
                        ...
                except KeyError:
                    prediction[f"{date.day}.{date.month}"] = {}

                prediction[f"{date.day}.{date.month}"][days_segments[a]] = {
                    "temp": temperatures[index],
                    "precip_chance": precipitation_chance[index],
                    "wind": wind[index],
                }
                a += 1
        else:
            continue
    return prediction
