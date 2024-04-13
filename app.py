from fastapi import FastAPI
from typing import List, Dict
from collections import defaultdict
from statistics import mean
from datetime import datetime, timedelta


from models import HourlyPrice, data, DataSource

app = FastAPI()

d = data(database="~/Downloads/dynamisch/")


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/hourly/{source}/{date}")
async def get_date(source: DataSource, date: datetime) -> HourlyPrice:
    """Retrieve the price at the specified date"""
    return d.get(source, start=date)


@app.get("/range/{source}/{start}/{end}")
async def get_range(
    source: DataSource, start: datetime, end: datetime
) -> List[HourlyPrice]:
    """Retrieve the prices in the specified range"""
    return list(d.range(source, start=start, end=end))


@app.post("/average/{items}")
def calc_average(hourly_rates: List[HourlyPrice]) -> Dict[str, float]:
    """Calculate the average hourly rate"""
    d = defaultdict(list)

    for item in hourly_rates:
        d[item.date.hour].append(item.price)

    return {str(hour): mean(d[hour]) for hour in d}


async def get_average_range(
    source: DataSource, start: datetime, end: datetime
) -> Dict[str, float]:
    data = await get_range(source, start, end)
    print(len(data))
    return calc_average(data)


@app.get("/average/day/{date}")
async def get_day_before(source: DataSource, date: datetime) -> Dict[str, float]:
    """Get the average for the day before the specified date"""
    end = date
    start = date - timedelta(hours=23)
    day = await get_average_range(source, start, end)
    return day


@app.get("/average/week/{date}")
async def get_week_before(source: DataSource, date: datetime) -> Dict[str, float]:
    """Get the average for the week before the specified date"""
    end = date
    start = date - timedelta(days=6)
    week = await get_average_range(source, start, end)
    return week


@app.get("/average/month/{date}")
async def get_month_before(source: DataSource, date: datetime) -> Dict[str, float]:
    """Get the average for the month before the specified date"""
    end = date
    start = date - timedelta(days=29)
    month = await get_average_range(source, start, end)
    return month


@app.get("/average/year/{date}")
async def get_year_before(source: DataSource, date: datetime) -> Dict[str, float]:
    """Get the average for the month before the specified date"""
    end = date
    start = date - timedelta(days=364)
    year = await get_average_range(source, start, end)
    return year
