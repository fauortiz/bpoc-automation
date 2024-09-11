import datetime
import re
from pendulum import DateTime as pendulumdatetime


def format_work(data):
    if not isinstance(data[0], str):
        raise Exception("ERROR: Task missing.")
    if not isinstance(data[1], int):
        raise Exception("ERROR: Percentage missing.")

    def format_percent_string(number):
        return f"{number}%"

    return f"- {data[0]} {format_percent_string(data[1])}"


def format_work_hipe(task, percentage, sep=","):
    if not isinstance(percentage, int):
        raise Exception("ERROR: Percentage missing.")
    return f"{task}{sep} {percentage}%"


def capitalize_first(s):
    return s[0].upper() + s[1:] if s else s


def get_week_range_string(week_dates):
    start = week_dates[min]
    end = week_dates[max]
    if start.month != end.month:
        formatted_date_range = (
            f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
        )
    else:
        formatted_date_range = f"{start.strftime('%B %d')}-{end.strftime('%d, %Y')}"

    def remove_leading_zeros(date_range_str):
        # Define the regex pattern to match leading zeros before days, not years
        pattern = r"\b0(\d{1,2})\b"
        return re.sub(pattern, r"\1", date_range_str)

    return remove_leading_zeros(formatted_date_range)


def verify_date(date):
    if isinstance(date, str):
        print(f"string date, parsing... {date}")
        date = datetime.strptime(date, "%b %d, %Y").date()

    if isinstance(date, pendulumdatetime):
        # print(f"pendulum date, parsing... {date}")
        date = date.naive().date()

    return date


def get_closer_year(month):
    """Determines the year of the given month that is closer to today's date.

    Args:
      month: The given month (1-12).

    Returns:
      The closer year.
    """
    today = datetime.date.today()
    current_year = today.year

    # print(month)  # 5
    # print(today.month)  # 9

    # Create date objects for the given month in the current year and next year
    current_year_date = datetime.date(current_year, month, 1)
    next_year_date = datetime.date(current_year + 1, month, 1)

    # Calculate the difference in days between today and the two possible dates
    diff_current_year = abs((current_year_date - today).days)
    diff_next_year = abs((next_year_date - today).days)

    # Return the year that is closer
    if diff_current_year <= diff_next_year:
        return current_year
    else:
        return current_year + 1


def get_task_timeframes(tasks):
    timeframes = {}
    for task, details in tasks.items():
        start_time = None
        end_time = None
        for date, minutes in details["dates"].items():
            current_time = datetime.datetime.combine(
                date, datetime.datetime.min.time()
            ).replace(
                hour=9
            )  # Start at 9 AM

            if start_time is None:
                start_time = current_time

            work_minutes = minutes
            while work_minutes > 0:
                # Check if we're at the lunch break
                if current_time.hour == 12:
                    current_time = current_time.replace(hour=13)  # Skip to 1 PM

                # Calculate available minutes until next break or end of day
                if current_time.hour < 12:
                    available_minutes = min(
                        work_minutes,
                        (12 - current_time.hour) * 60 - current_time.minute,
                    )
                else:
                    available_minutes = min(
                        work_minutes,
                        (18 - current_time.hour) * 60 - current_time.minute,
                    )

                current_time += datetime.timedelta(minutes=available_minutes)
                work_minutes -= available_minutes

                if current_time.hour >= 18:  # If we've reached or passed 6 PM
                    current_time = datetime.datetime.combine(
                        date + datetime.timedelta(days=1), datetime.datetime.min.time()
                    ).replace(hour=9)

            end_time = current_time

        timeframes[task] = (start_time, end_time)

    return timeframes


def format_for_spreadsheet(tasks):
    output = ""
    for task, details in tasks.items():
        start_date = details["begin"].date().strftime("%Y-%m-%d")
        end_date = details["end"].date().strftime("%Y-%m-%d")
        start_time = details["begin"].strftime("%H:%M")
        end_time = details["end"].strftime("%H:%M")
        output += f"Complete\t{start_date}\t{end_date}\t{start_time}\t{end_time}\t\t\t{task}\n"
    return output
