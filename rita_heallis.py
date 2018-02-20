"""Rita"""

import os
from functools import partial, singledispatch
from datetime import time, datetime
import calendar
import re

import pandas as pd
import numpy as np
import click

ALL = slice(None)
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
WELCOME_MSG = """Hi, I'm Rita.
I'm here to help you let everyone know when you can make it to your meeting!
To do so, I will ask you a couple of simple questions.
Most of them have default answers (in square brackets) that you can accept by just hitting "Enter".
If at any time you aren't sure how to answer, type "h" or "help" in the prompt.
"""
INTERVAL_HELP = """
You specify your availability either in time intervals or by typing "never" or "always".
One interval is a pair of integers between 9 and 19 separated by a space.
Note that the second digit is when the availability ends!
You can specify multiple intervals, separating them by spaces.

E.g. this input
9 13 14 19
basically means you are free all day except a break between 1pm and 2pm.
"""
DATE_HELP = """
You can provide multiple dates separated by spaces.
"""
PATTERNS_MSG = """
That's the preliminaries out of the way, yay!
In order to most efficiently record your availability, I will ask you for 'patterns' in your schedule.
This captures timeslots that occur on multiple days.
Subsequent patterns you provide will override earlier ones.
For instance, right now I assume that every day of the month you are available: "{}".
You can refine this by giving me more specific patterns.
"""

prompt_newline = partial(click.prompt, prompt_suffix="\n", value_proc=str.strip)
confirm_yes = partial(click.confirm, default=True)


@singledispatch
def help_requested(response):
    raise TypeError("Can't handle this type: {}".format(type(response)))


@help_requested.register(bool)
def bool_response(response):
    return False


@help_requested.register(str)
def bool_response(response):
    return bool(response and re.match("h(?:elp)?!?", response))


def pause_for_help(prompt_func, help_message, out=click.echo):
    """Keeps asking user for response and printing help message if requested."""
    while True:
        response = prompt_func()
        if help_requested(response):
            out(help_message)
            continue
        return response


def main():
    click.echo(WELCOME_MSG)
    name = pause_for_help(
        partial(prompt_newline, "Please enter your name:"),
        ("Can't start with a digit, "
         "otherwise any sequence of alphanumeric characters should work."))

    today = datetime.now()
    month = today.month + 1
    if not confirm_yes("We will check your availability for {}. Is that ok?".format(
            calendar.month_name[month])):
        month = int(
            pause_for_help(
                partial(prompt_newline, "Please enter a number for the month you'd like to plan."),
                "What you'd expect: any integer between 1 and 12 should work ;)"))

    table = init_availability(today.year, month, name)

    free_by_default = confirm_yes("I will by default assume that you are free all day."
                                  " If you're generally more often busy all day, say no.")
    global_default = "always" if free_by_default else "never"
    # makes more sense to have pattern default be the opposite from global
    pattern_default = "never" if free_by_default else "always"
    # we also need to update the table
    if free_by_default:
        table.loc[((ALL, ALL, ALL), ALL)] = 1

    click.echo(PATTERNS_MSG.format(global_default))

    while confirm_yes('Would you like to enter a new pattern?'):
        dates = parse_dates(
            pause_for_help(
                partial(prompt_newline, "What date(s) does this pattern apply?", default='All'),
                DATE_HELP))
        times = parse_intervals(
            pause_for_help(
                partial(
                    prompt_newline,
                    "What times are you free in this pattern?",
                    default=pattern_default), INTERVAL_HELP))
        for start, end in times:
            table.loc[((dates, slice(start, end - 1), ALL), ALL)] = 1

    default_path = os.path.join(os.path.expanduser("~"), "{}_availability.csv".format(name))
    csv_path = pause_for_help(
        partial(
            click.prompt,
            "Where should I save your CSV?",
            default=click.format_filename(default_path)), "This is pretty self-explanatory...")
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


def parse_intervals(times_input: str):
    if times_input == 'never':
        return []
    if times_input == 'always':
        return [(9, 19)]
    pairs = times_input.strip().split()
    if len(pairs) % 2 != 0:
        raise RitaInputError(
            "I don't know what to do with an odd number of times: {}".format(len(pairs)))
    time_pairs = [int(t) for t in pairs]
    return list(zip(time_pairs[::2], time_pairs[1::2]))


def parse_dates(dates_input: str):
    if dates_input == "None":
        return []
    if dates_input == 'All':
        return ALL
    dates = dates_input.strip().split()
    return [int(d) for d in dates]


if __name__ == '__main__':
    main()
