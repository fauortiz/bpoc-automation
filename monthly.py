#!/usr/bin/env python3

from collections import OrderedDict
import sys
from numbers_parser import Document
import datetime
import calendar
import os
import pyperclip
from utils import verify_date, get_closer_year, format_for_spreadsheet, count_breaks
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
        desktop_path = os.path.join(home_dir, "Desktop")
        doc = Document(os.path.join(desktop_path, "reports.numbers"))

        sheet = doc.sheets[0]
        table = sheet.tables[0]

        if len(args[0]) != 1 or int(args[0][0]) not in range(1, 13):
            raise Exception("ERROR: Invalid month number.")

        month_number = int(args[0][0])
        year = get_closer_year(month_number)
        month_start = datetime.datetime(
            year, month_number, 1
        )  # Set day to 1 for consistency
        days_in_month = calendar.monthrange(year, month_number)[1]
        month_end = month_start + datetime.timedelta(days=days_in_month - 1)
        month_start = month_start.date()
        month_end = month_end.date()

        all_tasks = []
        unique_tasks = OrderedDict()
        unique_dates = OrderedDict()

        # process input
        for row in range(table.num_rows):
            date = table.cell(row, 0).value

            if date is None:
                continue

            date = verify_date(date)

            # only use the indicated month's dates
            if not month_start <= date <= month_end:
                continue

            task = table.cell(row, 1).value
            percentage = table.cell(row, 2).value
            weight = table.cell(row, 3).value

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

        # get total minutes per unique task
        for task_data in all_tasks:
            date = task_data["date"]
            task = task_data["task"]
            weight = task_data["weight"]

            total_mins_for_day = unique_dates[date]["total_mins"]
            task_mins = round(
                (weight / unique_dates[date]["total_weight"]) * total_mins_for_day
            )
            # task_data["mins"] = task_mins
            unique_tasks[task]["total_mins"] += task_mins

        # # populate the 'dates' object with date: minutes spent for that date.
        # #   Example:
        # #   {'Work on C03 v3': {
        # #           'completion': 100.0,
        # #           'total_mins': 560,
        # #           'dates': {Date(2024, 9, 2): 480, ...},
        # #   }

        # dates_keys = list(unique_dates.keys())
        # dates_index = 0
        # # for each task, in order...
        # for task in unique_tasks:
        #     while unique_tasks[task]["total_mins"] > 0:
        #         task_mins = unique_tasks[task]["total_mins"]
        #         # print(task, task_mins)
        #         date = dates_keys[dates_index]
        #         # print(date)
        #         date_mins = unique_dates[date]["total_mins"]
        #         # print(date_mins)

        #         date_mins_after = date_mins - task_mins

        #         if date_mins_after == 0:
        #             # print("equal, next")
        #             # the date is filled up, the task is completed on that day.
        #             # record date and mins into unique_tasks, move to the next date, move to the next task
        #             unique_tasks[task]["dates"][date] = task_mins
        #             unique_tasks[task]["total_mins"] = 0

        #             unique_dates[date]["total_mins"] = 0
        #             dates_index += 1
        #             break
        #         if date_mins_after > 0:
        #             # print("greater, stay on date")
        #             # the date still has space, the task is completed on that day.
        #             # record date and mins into unique_tasks, move to the next task, stay on same day, but update its remaining mins.
        #             unique_tasks[task]["dates"][date] = task_mins
        #             unique_tasks[task]["total_mins"] = 0

        #             unique_dates[date]["total_mins"] = date_mins_after
        #             break
        #         if date_mins_after < 0:
        #             # print("less then, carry over task")
        #             # the date is filled up, the task is not yet completed.
        #             # get mins left for the task, save that.
        #             # record date and mins into unique_tasks, stay on this task, move to next day.
        #             remaining_task_mins = task_mins - date_mins
        #             unique_tasks[task]["dates"][date] = date_mins
        #             unique_tasks[task]["total_mins"] = remaining_task_mins

        #             unique_dates[date]["total_mins"] = 0
        #             dates_index += 1

        # REFERENCE
        # pprint(unique_tasks)

        def convert_date_to_workdt(list, date, time=None):
            if time:
                return WorkDateTime(
                    list, date.year, date.month, date.day, time.hour, time.minute
                )
            return WorkDateTime(list, date.year, date.month, date.day)

        timeframes = {}

        list_of_date_keys = list(unique_dates.keys())

        # pprint(list_of_date_keys)

        start_date = list_of_date_keys[0]
        current_workdt = convert_date_to_workdt(list_of_date_keys, start_date)
        for task in unique_tasks:
            if current_workdt.datetime.hour == 18:
                current_workdt.adjust_to_next_workday()
                print(current_workdt)
            # set the current task's start as the previous end datetime

            total_mins = unique_tasks[task]["total_mins"]
            next_workdt = current_workdt + datetime.timedelta(minutes=total_mins)

            break_count, _, _ = count_breaks(
                current_workdt.datetime, next_workdt.datetime, list_of_date_keys
            )
            # print(break_count, current_workdt.datetime, a, next_workdt.datetime, b)

            next_workdt = next_workdt + datetime.timedelta(hours=break_count)

            total_workdays = total_mins / 60 / 8
            timeframes[task] = (
                current_workdt.datetime,
                next_workdt.datetime,
                total_workdays,
            )

            # set the start point for the next iteration
            # current_workdt = current_workdt + datetime.timedelta(minutes=total_mins)
            current_workdt = next_workdt

        # pprint(timeframes)

        for task in unique_tasks:
            unique_tasks[task]["begin"] = timeframes[task][0]
            unique_tasks[task]["end"] = timeframes[task][1]
            unique_tasks[task]["duration"] = timeframes[task][2]

        monthly_string = format_for_spreadsheet(unique_tasks)
        pyperclip.copy(monthly_string)

        month_name = calendar.month_name[month_number]
        print(f"Monthly report for {month_name} {year} copied to clipboard!")

    except Exception as e:
        raise (e)


if __name__ == "__main__":
    make_monthly_report(sys.argv[1:])

# TODO possible bugs:
# 1. it might show a start or end time within the lunch break, maybe?
