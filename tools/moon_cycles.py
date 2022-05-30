#!/usr/bin/env python3

import sys
from math import gcd
from os.path import dirname
sys.path.append(f"{dirname(__file__)}/..")

from app import create_app  # noqa: E402
from app.calendar.models import Epoch, Month, Moon  # noqa: E402
from app.calendar.helpers import gen_calendar_stats  # noqa: E402

# TODO: delta should come from archivar
delta = 2


# math.lcm is only availabile for python > 3.9
def lcm(a, b):
    return abs(a*b) // gcd(a, b)


# TODO: should be an archivar helper function
def calc_timestamp(epoch_id, year, month_id, day):
    timestamp = 0
    stats = gen_calendar_stats()

    epoch = Epoch.query.filter_by(order=epoch_id).first()
    years = epoch.years_before + (year - 1)

    month = Month.query.filter_by(order=month_id).first()
    days_into_year = month.days_before + day

    timestamp = years * stats["days_per_year"] + days_into_year

    return timestamp


# TODO: should be an archivar helper function
def date_str(timestamp):
    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days_per_year = months[-1].days_before + months[-1].days

    # find epoch
    total_years = int(timestamp / days_per_year)
    epoch_idx = -1

    for i, e in enumerate(epochs):
        if total_years < e.years_before:
            epoch_idx = max(0, i - 1)
            break

    epoch = epochs[epoch_idx]

    # find year
    year = total_years - epoch.years_before + 1

    # find month
    days_into_year = timestamp - (days_per_year * total_years)
    month_idx = -1

    for i, m in enumerate(months):
        if days_into_year <= m.days_before:
            month_idx = max(0, i - 1)
            break

    month = months[month_idx]

    # find day
    day = days_into_year - month.days_before

    return f"{day} of {month.name}, {year} {epoch.name}"


def is_full_moon(moon, timestamp):
    p = moon.calc_phase(timestamp)*100
    return (p <= (0 + delta) or p >= (100 - delta))


def is_new_moon(moon, timestamp):
    p = moon.calc_phase(timestamp)*100
    return (p >= (50 - delta) and p <= (50 + delta))


def find_moon_cycles(moons, start_date):
    # number of days to check via least common multiple of all phase lengths
    total_phase = 1
    for moon in moons:
        total_phase = lcm(total_phase, moon.phase_length)
    print(f"phase length: {total_phase}")

    for i in range(start_date, start_date + total_phase):
        fullmoon = True
        newmoon = True

        for moon in moons:
            if not is_full_moon(moon, i):
                fullmoon = False

            if not is_new_moon(moon, i):
                newmoon = False

            # skip other moons if no chance of success
            if not (fullmoon or newmoon):
                continue

        if fullmoon:
            print(f"total full moon @ {i}: {date_str(i)}")

        if newmoon:
            print(f"total new moon @ {i}: {date_str(i)}")


# brute force the dates of the next total full and new moons from a given starting date
if __name__ == "__main__":
    app = create_app()
    app.app_context().push()

    moons = Moon.query.order_by(Moon.id.asc()).all()

    epoch = 1
    year = 1

    # TODO argparse, add month and day
    if len(sys.argv) == 3:
        epoch = int(sys.argv[1])
        year = int(sys.argv[2])

    # epoch, year, month, day
    start_date = calc_timestamp(epoch, year, 1, 1)
    print(f"start date: {date_str(start_date)}")

    find_moon_cycles(moons, start_date)
