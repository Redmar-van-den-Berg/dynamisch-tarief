#!/usr/bin/env python3

import argparse
import os
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class DataSource(Enum):
    ELECTRIC = "netto"
    ELECTRIC_WHOLESALE = "wholesale"
    GAS = "gas.netto"
    GAS_WHOLESALE = "gas.wholesale"

class data(BaseModel):
    database: str

    def get(self, source: DataSource, start: datetime) -> float:
        date = start
        fname = self.fname(source, date)
        with open(fname) as fin:
            # The hour we are interested in
            requested = f"{date:%H}:00"
            for line in fin:
                hour, value = line.strip('\n').split(",")
                if hour == requested:
                    return float(value)
            else:
                raise RuntimeError

    def fname(self, source: DataSource, date: datetime) -> str:
        dir = os.path.expanduser(self.database)
        fname = f"{source.value}.{date:%m-%d-%Y}.csv"
        return os.path.join(dir, fname)

def main(database: str, dtime: datetime, source: DataSource) -> None:
    d = data(database=database)
    print(d.get(source, dtime))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", default="~/Downloads/dynamisch/")
    parser.add_argument("--dtime", default=datetime.now())
    parser.add_argument("--source", type=str, default=DataSource.ELECTRIC, choices = [x.value for x in DataSource])

    args = parser.parse_args()
    args.source = DataSource(args.source)

    main(args.database, args.dtime, args.source)

