#!/usr/bin/env python3

import sys
from numbers_parser import Document
from datetime import datetime
import time
import os
import pyautogui
from utils import verify_date


def make_daily_task(*args):
    DAIRY_ARG = "dairy"

    try:
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        doc = Document(os.path.join(desktop_path, "reports.numbers"))
        sheet = doc.sheets[0]
        table = sheet.tables[0]

        todays_work = []
        today = datetime.today().date()
        for row in range(table.num_rows):
            date = table.cell(row, 0).value

            if date is None:
                continue

            date = verify_date(date)

            if date != today:
                continue

            percentage = table.cell(row, 2).value
            percentage = int(percentage) if percentage is not None else 100

            task = table.cell(row, 1).value
            hours = table.cell(row, 6).value
            hours = int(hours) if hours is not None else 1

            todays_work.append((task, hours))

        print("Starting in 2 seconds...")

        time.sleep(2)
        is_dairy = args and args[0] and args[0][0] == DAIRY_ARG
        delimiter = "enter" if is_dairy else "tab"
        lunchbreak_counter = 0
        for work in todays_work:
            task, hours = work
            for _ in range(hours):
                pyautogui.write(task)
                pyautogui.press(delimiter)
                lunchbreak_counter += 1
                if lunchbreak_counter == 3 and is_dairy:
                    pyautogui.press(["enter", "enter", "enter"])

        print("Done typing today's work!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    make_daily_task(sys.argv[1:])
