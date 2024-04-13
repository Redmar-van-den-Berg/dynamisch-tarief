#!/usr/bin/env python3

import argparse
import os, sys
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
from typing import Iterator


class DataSource(Enum):
    ELECTRIC = "netto"
    ELECTRIC_WHOLESALE = "wholesale"
    GAS = "gas.netto"
    GAS_WHOLESALE = "gas.wholesale"


class HourlyPrice(BaseModel):
    date: datetime
    price: float


class data(BaseModel):
    database: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "netto",
                    "hour": str(
                        datetime.now()
                    ),  # .replace(minute=0, second=0, microsecond=0))
                }
            ]
        }
    }

    def get(self, source: DataSource, start: datetime) -> HourlyPrice:
        """Get the data for a range of dates"""
        return self._get(source, start.replace(minute=0, second=0, microsecond=0))

    def _get(self, source: DataSource, date: datetime) -> HourlyPrice:
        fname = self.fname(source, date)

        if not os.path.exists(fname):
            raise RuntimeError(f"File {fname} not found")
        with open(fname) as fin:
            # The hour we are interested in
            requested = f"{date:%H}:00"
            for line in fin:
                hour, value = line.strip("\n").split(",")
                if hour == requested:
                    return HourlyPrice(date=date, price=float(value))
            else:
                raise RuntimeError(f"Hour {requested} not found in {fname}")

    def range(
        self, source: DataSource, start: datetime, end: datetime
    ) -> Iterator[HourlyPrice]:
        """Fetch hourly rates for the specified date range"""
        current_date = start
        one_hour = timedelta(hours=1)

        while current_date <= end:
            try:
                data = self.get(source, current_date)
            except RuntimeError as e:
                print(e, file=sys.stderr)
            else:
                yield data

            current_date += one_hour

    def fname(self, source: DataSource, date: datetime) -> str:
        dir = os.path.expanduser(self.database)
        fname = f"{source.value}.{date:%m-%d-%Y}.csv"
        return os.path.join(dir, fname)


def main(database: str, dtime: datetime, source: DataSource) -> None:
    d = data(database=database)

    # We only have date and hours, we set the rest to zero
    dtime = dtime.replace(minute=0, second=0, microsecond=0)

    last_week = dtime - timedelta(days=7)

    for price in d.range(source, last_week, dtime):
        print(price)

    # print(m.model_dump_json())


if __name__ == "__main__":

    def valid_date(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%d")

    parser = argparse.ArgumentParser()

    parser.add_argument("--database", default="~/Downloads/dynamisch/")
    parser.add_argument("--dtime", default=datetime.now(), type=valid_date)
    parser.add_argument(
        "--source",
        type=str,
        default=DataSource.ELECTRIC,
        choices=[x.value for x in DataSource],
    )

    args = parser.parse_args()
    args.source = DataSource(args.source)
    print(args)

    main(args.database, args.dtime, args.source)
