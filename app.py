from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from collections import defaultdict
from statistics import mean
from datetime import datetime, timedelta
import argparse
import uvicorn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO


from models import HourlyPrice, data, DataSource

app = FastAPI()

def draw(data: Dict[str, Any]) -> str:
    # Add in duplicate data for 23:00 under 24:00, so the stepped plot ends at 24:00
    for timespan in data:
        data[timespan]["24:00"] = data[timespan]["23:00"]

    df = pd.DataFrame(data)
    print(df)

    # Min is 90% of min value
    ymin = df.to_numpy().min()
    if ymin > 0:
        ymin *= 0.9
    else:
        ymin *= 1.1
    # Max is 110% of max value
    ymax = df.to_numpy().max()*1.10
    ax = df.plot(kind="line", drawstyle="steps-post", ylim=(ymin, ymax), figsize=(10, 5), xlim=(0,24))

    ax.xaxis.grid(True, which='both')
    ax.yaxis.grid(True, which='both')

    # Show grid line for every hour
    ax.set_xticks(np.arange(len(df)))

    # 'write' the figure as svg
    fake_file = StringIO()
    plt.savefig(fake_file, format="svg")
    fake_file.seek(0)

    return fake_file.read()

@app.get("/{source}", response_class=HTMLResponse)
async def root(source: DataSource):
    today = datetime.now().replace(hour=23)
    day = await get_day_before(source, today)
    week = await get_week_before(source, today)
    month = await get_month_before(source, today)
    year = await get_year_before(source, today)

    data = {
        "day": day,
        "week": week,
        "month": month,
        "year": year
    }
    return draw(data)


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

    return {f"{str(hour).zfill(2)}:00": mean(d[hour]) for hour in d}


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", required=True, help="Folder that contains the dynamic prices")
    parser.add_argument("--host", required=True, help="Host to listen to")

    args = parser.parse_args()
    d = data(database=args.database)
    uvicorn.run(app, host=args.host)
