from fastapi import FastAPI, Body
from typing import List

from models import HourlyPrice, data, DataSource, datetime

app = FastAPI()

d = data(database="~/Downloads/dynamisch/")


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/hourly/{source}/{date}")
async def get_date(source: DataSource, date: datetime) -> HourlyPrice:
    return d.get(source, start=date)


@app.get("/range/{source}/{start}/{end}")
async def get_range(
    source: DataSource, start: datetime, end: datetime
) -> List[HourlyPrice]:
    return list(d.range(source, start=start, end=end))
