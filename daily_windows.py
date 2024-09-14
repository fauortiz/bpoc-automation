#!/usr/bin/env python3

import sys
import pyexcel_ods
from datetime import datetime
import os
import pyperclip
from utils import format_work, capitalize_first, format_work_hipe, verify_date


def make_daily_task(*args):
    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "OneDrive", "Desktop")
        calc_path = os.path.join(desktop_path, "reports.ods")

        if len(args) == 0:
            raise Exception("ERROR: Missing tasks for tomorrow.")

        # Read the .ods file
        data = pyexcel_ods.get_data(calc_path)
        sheet = data[list(data.keys())[0]]  # Get the first sheet

        todays_work = []
        today = datetime.today().date()

        for row in sheet:
            if len(row) < 3:
                continue

            date = row[0]

            if date is None:
                continue

            date = verify_date(date)

            if date != today:
                continue

            task = row[1]
            percentage = int(row[2])

            todays_work.append((task, percentage))

        today_header = "■Today's work"
        formatted_today = "\n".join([f"{format_work(work)}" for work in todays_work])

        tomorrow_header = "■Tomorrow's work schedule"
        formatted_tomorrow = "\n".join([f"- {capitalize_first(task)}" for task in args])

        formatted_problems = "■Problem\n- None in particular"

        lrt_daily = f"{today_header}\n{formatted_today}\n{tomorrow_header}\n{formatted_tomorrow}\n{formatted_problems}"
        hipe_daily = "\n".join(
            [f"{format_work_hipe(work[0], work[1])}" for work in todays_work]
        )

        pyperclip.copy(lrt_daily)

        print(lrt_daily)
        print("\nLRT daily report copied to clipboard! ...For HiPE daily report:\n")
        print(hipe_daily)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    make_daily_task(*sys.argv[1:])