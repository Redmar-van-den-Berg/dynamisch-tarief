from fastapi import FastAPI, Body
from typing import List, Dict
from collections import defaultdict
from statistics import mean

from models import HourlyPrice, data, DataSource, datetime

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
async def calc_average(hourly_rates: List[HourlyPrice]) -> Dict[str, float]:
    """Calculate the average hourly rate"""
    d = defaultdict(list)

    for item in hourly_rates:
        d[item.date.hour].append(item.price)

    return {str(hour): mean(d[hour]) for hour in d}
