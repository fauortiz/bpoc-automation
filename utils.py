import datetime
import re
from pendulum import DateTime as pendulumdatetime


def format_work(data):
    if not isinstance(data[0], str):
        raise Exception("ERROR: Task missing.")
    if not isinstance(data[1], float):
        raise Exception("ERROR: Percentage missing.")

    def format_percent_string(number):
        return f"{number * 100:.0f}%"

    return f"- {data[0]} {format_percent_string(data[1])}"


def format_work_hipe(task, perc, sep=","):
    if isinstance(perc, float):
        fperc = f"{perc * 100:.0f}%"
    else:
        raise Exception("ERROR: Percentage missing.")
    return f"{task}{sep} {fperc}"


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
