#!/usr/bin/env python3

from collections import OrderedDict
import sys
import pyexcel_ods
import datetime
import calendar
import os
import pyperclip
from utils import verify_date, get_closer_year, format_for_spreadsheet
from pprint import pprint
from WorkDateTime import WorkDateTime


def make_monthly_report(*args):
    """
    get list of unique tasks
        - for every row in reports:
            - save each task, in order. List of Dicts.
                [ {date, task, weight}, ... ]
            - save each unique task & percent completion, in order. ordered Dicts.
                { task: highest_percentage, ... }
            - save weights & hours per day, in order. ordered Dict.
                { workday: { total_weight, total_mins=480 }, ... }

    get the exact days you went to work (off days removed)
        - for each task in tasks:
            - get total mins per task per day (using weight / total_weight * total_mins).
            - add it to all_tasks, as mins, below:
            all_tasks = [ { date: 1234, task: "asdf", weight: 1, mins: 555 }, ... ]
            - sum hours per unique task.
            unique_tasks = {
                    task: {
                    completion: 100%,
                    total_mins: 5555, # sum of mins above
                    },
                    ...
                }

    distribute each task along the total hours of the month.

    paste into a CSV to fit rows in? tabs and enters
    """
    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "OneDrive" , "Desktop")
        calc_path = os.path.join(desktop_path, "reports.ods")

        if len(args) == 0 or int(args[0]) not in range(1, 13):
            raise Exception("ERROR: Invalid month number.")

        month_number = int(args[0])
        year = get_closer_year(month_number)
        month_start = datetime.datetime(year, month_number, 1)  # Set day to 1 for consistency
        days_in_month = calendar.monthrange(year, month_number)[1]
        month_end = month_start + datetime.timedelta(days=days_in_month - 1)
        month_start = month_start.date()
        month_end = month_end.date()

        all_tasks = []
        unique_tasks = OrderedDict()
        unique_dates = OrderedDict()

        # Read the .ods file
        data = pyexcel_ods.get_data(calc_path)
        sheet = data[list(data.keys())[0]]  # Get the first sheet

        # Process input
        for row in sheet:
            if len(row) < 4:
                continue

            date = row[0]

            if date is None:
                continue

            date = verify_date(date)

            # Only use the indicated month's dates
            if not month_start <= date <= month_end:
                continue

            task = row[1]
            percentage = row[2]
            weight = row[3]

            all_tasks.append(
                {
                    "date": date,
                    "task": task,
                    "weight": weight,
                }
            )

            if task not in unique_tasks:
                unique_tasks[task] = {
                    "completion": percentage,
                    "total_mins": 0,
                    "dates": {},
                    "begin": None,
                    "end": None,
                }
            else:
                if unique_tasks[task]["completion"] < percentage:
                    unique_tasks[task]["completion"] = percentage

            if date not in unique_dates:
                unique_dates[date] = {
                    "total_weight": weight,
                    "total_mins": 480,
                }
            else:
                unique_dates[date]["total_weight"] += weight

        # Get total minutes per unique task
        for task_data in all_tasks:
            date = task_data["date"]
            task = task_data["task"]
            weight = task_data["weight"]

            total_mins_for_day = unique_dates[date]["total_mins"]
            task_mins = round(
                (weight / unique_dates[date]["total_weight"]) * total_mins_for_day
            )
            unique_tasks[task]["total_mins"] += task_mins

        def convert_date_to_workdt(list, date, time=None):
            if time:
                return WorkDateTime(
                    list, date.year, date.month, date.day, time.hour, time.minute
                )
            return WorkDateTime(list, date.year, date.month, date.day)

        timeframes = {}

        date_index = 0
        list_of_date_keys = list(unique_dates.keys())

        start_date = list_of_date_keys[date_index]
        current_workdt = convert_date_to_workdt(list_of_date_keys, start_date)
        for task in unique_tasks:
            if task not in timeframes:
                total_mins = unique_tasks[task]["total_mins"]
                next_workdt = current_workdt + datetime.timedelta(minutes=total_mins)
                total_workdays = total_mins / 60 / 9
                timeframes[task] = (
                    current_workdt.datetime,
                    next_workdt.datetime,
                    total_workdays,
                )

                current_workdt = current_workdt + datetime.timedelta(minutes=total_mins)

        for task in unique_tasks:
            unique_tasks[task]["begin"] = timeframes[task][0]
            unique_tasks[task]["end"] = timeframes[task][1]
            unique_tasks[task]["duration"] = timeframes[task][2]

        monthly_string = format_for_spreadsheet(unique_tasks)
        pyperclip.copy(monthly_string)

        month_name = calendar.month_name[month_number]
        print(f"Monthly report for {month_name} {year} copied to clipboard!")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    make_monthly_report(*sys.argv[1:])