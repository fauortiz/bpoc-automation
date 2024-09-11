#!/usr/bin/env python3

import sys
from numbers_parser import Document
from datetime import datetime
import os
import pyperclip
from utils import format_work, capitalize_first, format_work_hipe, verify_date


def make_daily_task(*args):
    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        doc = Document(os.path.join(desktop_path, "reports.numbers"))

        sheet = doc.sheets[0]
        table = sheet.tables[0]
        task_tomorrow = args[0]
        if len(task_tomorrow) == 0:
            raise Exception("ERROR: Missing task for tomorrow.")

        todays_work = []
        today = datetime.today().date()
        for row in range(table.num_rows):
            date = table.cell(row, 0).value

            if date is None:
                continue

            date = verify_date(date)

            if date != today:
                continue

            task = table.cell(row, 1).value
            percentage = int(table.cell(row, 2).value)

            todays_work.append((task, percentage))

        today_header = "■Today's work"
        formatted_today = "\n".join([f"{format_work(work)}" for work in todays_work])

        tomorrow_header = "■Tomorrow's work schedule"
        dashless_formatted_tomorrow = capitalize_first(" ".join(task_tomorrow))
        capitalized_formatted_tomorrow = dashless_formatted_tomorrow
        formatted_tomorrow = "- " + capitalized_formatted_tomorrow

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
    make_daily_task(sys.argv[1:])
