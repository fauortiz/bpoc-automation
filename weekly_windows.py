#!/usr/bin/env python3

from collections import OrderedDict
import sys
import pyexcel_ods
import datetime
import os
import pyperclip
from utils import get_week_range_string, format_work_hipe, verify_date


def make_weekly_task(start_date=None, end_date=None):
    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "OneDrive", "Desktop")
        calc_path = os.path.join(desktop_path, "reports.ods")

        # Read the .ods file
        data = pyexcel_ods.get_data(calc_path)
        sheet = data[list(data.keys())[0]]  # Get the first sheet

        today = datetime.datetime.now().date()

        if start_date is None or end_date is None:
            start_of_this_week = today + datetime.timedelta(days=-today.weekday())
            end_of_this_week = start_of_this_week + datetime.timedelta(days=4)
        else:
            start_of_this_week = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_of_this_week = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        # Check if today is within the specified date range
        if not (start_of_this_week <= today <= end_of_this_week):
            print(f"Today's date {today} is not within the specified date range {start_of_this_week} to {end_of_this_week}.")
            return

        week_dates = [start_of_this_week + datetime.timedelta(days=i) for i in range((end_of_this_week - start_of_this_week).days + 1)]

        weekly_tasks = {}
        week_range = {"min": datetime.date.max, "max": datetime.date.min}

        for row in sheet:
            if len(row) < 3:
                continue

            date = row[0]

            if date is None:
                continue

            date = verify_date(date)

            if not any(date == weekdate for weekdate in week_dates):
                continue

            if week_range["min"] > date:
                week_range["min"] = date
            if week_range["max"] < date:
                week_range["max"] = date

            task = row[1]
            percentage = int(row[2])

            if task not in weekly_tasks:
                weekly_tasks[task] = percentage
            else:
                weekly_tasks[task] = max(weekly_tasks[task], percentage)

        week_range_str = get_week_range_string(week_range)
        title = "LRTechs"
        hipe_weekly = "\n".join(
            [f"- {format_work_hipe(task, perc, ':')}" for task, perc in weekly_tasks.items()]
        )
        weekly_string = f"{week_range_str}\n{title}\n{hipe_weekly}"

        pyperclip.copy(weekly_string)
        print(weekly_string)
        print("\nWeekly report copied to clipboard!")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        make_weekly_task(sys.argv[1], sys.argv[2])
    else:
        make_weekly_task()