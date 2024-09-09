#!/usr/bin/env python3

import sys
from numbers_parser import Document
import datetime
import os
import pyperclip
from utils import get_week_range_string, format_work_hipe, verify_date


def make_monthly_report(*args):
    """
    get list of unique tasks (input should be sorted)
        - get total hours per task per day (using weights).
        - sum hours per unique task.
        - save highest percentage per unique task.
        - get the exact days with work
        - distribute each task along the total hours of the month, rounded.
        - paste into a CSV to fit rows in? tabs and enters
    """
    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        doc = Document(os.path.join(desktop_path, "reports.numbers"))

        sheet = doc.sheets[0]
        table = sheet.tables[0]
        month_number = args[0]

        start_of_this_week = today + datetime.timedelta(days=-today.weekday())
        week_dates = [start_of_this_week + datetime.timedelta(days=i) for i in range(5)]

        weekly_tasks = {}
        week_range = {min: datetime.date.max, max: datetime.date.min}

        for row in range(table.num_rows):
            date = table.cell(row, 0).value

            if date is None:
                continue

            date = verify_date(date)

            if not any(date == weekdate for weekdate in week_dates):
                continue

            if week_range[min] > date:
                week_range[min] = date
            if week_range[max] < date:
                week_range[max] = date

            task = table.cell(row, 1).value
            percentage = table.cell(row, 2).value
            weight = table.cell(row, 3).value

            if task not in weekly_tasks:
                weekly_tasks[task] = percentage
            else:
                weekly_tasks[task] = max(weekly_tasks[task], percentage)

        week_range_str = get_week_range_string(week_range)
        title = "LRTechs"
        hipe_weekly = "\n".join(
            [f"- {format_work_hipe(task, perc, ":")}" for task, perc in weekly_tasks.items()]
        )
        weekly_string = f"{week_range_str}\n{title}\n{hipe_weekly}"

        pyperclip.copy(monthly_string)
        print("\nMonthly report copied to clipboard!")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    make_monthly_report(sys.argv[1:])
