"""Rita"""

import os
from functools import partial
from datetime import time, datetime
import calendar

import pandas as pd
import numpy as np
import click

ALL = slice(None)
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
WELCOME_MSG = """Hi, I'm Rita.
I'm here to help you let everyone know when you can make it to your meeting!
To do so, I will ask you a couple of simple questions.

The only time the formatting of your answer matters is when I need you to provide multiple items.
For, example, to tell me that you are free between 9am and 1pm, enter these two times in the prompt:
9 13
If you happen to be free for two slices of time on one particular day,
you can use a space again to separate the intervals, like so:
9 13 15 19
This says you're available from 9am to 1pm and again from 3pm till 7pm.

Please note several things:
- We use the 24hour clock.
- Only hours from 9 to 19 are considered.
- The interval end (second hour) is *not* part of the interva1!

For each day of the week we first look at your usual schedule and then at "exceptional" cases.
If you don't have a regular schedule on that day, ignore that part and fill out every date individually.
"""

prompt_newline = partial(click.prompt, prompt_suffix="\n", value_proc=str.strip)


def main():
    click.echo(WELCOME_MSG)
    name = prompt_newline("Please enter your name:")

    today = datetime.now()
    month = today.month + 1
    if not click.confirm(
            "We will check your availability for {}. Is that ok?".format(
                calendar.month_name[month]),
            default=True):
        month = int(
            prompt_newline("Please enter a number from [1-12] for the month you'd like to plan."))

    table = init_availability(today.year, month, name)

    for day in DAYS:
        click.echo("Ok, let's deal with {}.".format(day))
        regular_times = parse_intervals(
            prompt_newline(("What times are you usually free on {}s? "
            "You can specify an hour from the range [9-19]. "
            "The end of the interval is not included in the interval!").format(day), default="never"))
        for start, end in regular_times:
            table.loc[((ALL, slice(start, end - 1), day), ALL)] = 1

        weekday_dates = table.loc[((ALL, ALL, day), ALL)].index.unique().levels[0]
        weekday_options = " ".join(str(d) for d in weekday_dates)
        exceptions = parse_exceptions(
            prompt_newline(
                ('Any exceptions to this? Type one of these numbers {}.\n'
                "You can give more than one (separated by spaces) or just hit `Enter`").format(weekday_options),
                default="None"))
        for ex in exceptions:
            # we have to reset the availability for that day
            table.loc[((ex, ALL, ALL), ALL)] = 0
            # TODO check if the date is valid!
            ex_times = parse_intervals(
                prompt_newline(
                    "What times are you free on {}?".format(ex), default="never"))
            for start, end in ex_times:
                table.loc[((ex, slice(start, end - 1), ALL), ALL)] = 1

    default_path = os.path.join(os.path.expanduser("~"), "{}_availability.csv".format(name))
    csv_path = click.prompt(
        "Where should I save your CSV?", default=click.format_filename(default_path))
    table.to_csv(csv_path)


class RitaInputError(Exception):
    """When user gives Rita a bad input."""
    pass


def init_availability(year, month, name):
    """Create table of timeslots for the user to fill in."""
    cal = calendar.Calendar()
    intervals = list(range(9, 19))
    # we only want non-weekend days strictly in this month
    # Calendar.itermonthdates returns more than we need, so we exclude that stuff.
    dates = [dd for dd in cal.itermonthdates(year, month) if dd.month == month and dd.weekday() < 5]
    times = [t for _ in range(len(dates)) for t in intervals]
    dates_timed = [d for d in dates for _ in range(len(intervals))]
    week_days = [calendar.day_name[dd.weekday()] for dd in dates_timed]
    table = pd.DataFrame(
        {
            '{}_available'.format(name): np.zeros(len(dates_timed), dtype='int')
        },
        index=[[d.day for d in dates_timed], times, week_days])
    table.index.set_names(['date', 'time', 'weekday'], inplace=True)
    return table


def parse_time(input_time: str):
    # TODO: add some exception catching here?
    return time(int(input_time))


def parse_intervals(times_input: str):
    if times_input == 'never':
        return []
    pairs = times_input.strip().split()
    if len(pairs) % 2 != 0:
        raise RitaInputError(
            "I don't know what to do with an odd number of times: {}".format(len(pairs)))
    time_pairs = [int(t) for t in pairs]
    return list(zip(time_pairs[::2], time_pairs[1::2]))


def parse_exceptions(exceptions_input: str):
    if exceptions_input == "None":
        return []
    dates = exceptions_input.strip().split()
    return [int(d) for d in dates]


if __name__ == '__main__':
    main()
