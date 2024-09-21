import datetime
import re
from pendulum import DateTime as pendulumdatetime
import platform


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
        if platform.system() == "Windows":
            date = datetime.datetime.strptime(date, "%m/%d/%Y").date()
        elif platform.system() == "Darwin":
            date = datetime.strptime(date, "%m/%d/%y").date()
        else:
            raise NotImplementedError("Unsupported operating system")


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


def format_for_spreadsheet(tasks):
    output = ""
    for task, details in tasks.items():
        start_date = details["begin"].date().strftime("%Y-%m-%d")
        end_date = details["end"].date().strftime("%Y-%m-%d")
        start_time = details["begin"].strftime("%H:%M")
        end_time = details["end"].strftime("%H:%M")
        duration = details["duration"]
        output += f"Complete\t{start_date}\t{end_date}\t{start_time}\t{end_time}\t{duration}\t{duration}\t{task}\n"
    return output


def count_breaks(start_datetime, end_datetime, list_of_dates):
    # Define the time window for the break (12:00 PM to 1:00 PM)
    break_start_time = datetime.timedelta(hours=12)
    break_end_time = datetime.timedelta(hours=13)

    # Initialize the count of breaks
    break_count = 0

    # Store the final start and end datetime for output
    final_start_datetime = start_datetime
    final_end_datetime = end_datetime

    # Move through each day between the start and end datetimes
    current_day = start_datetime.date()
    end_day = end_datetime.date()

    # Loop through each day
    while current_day <= end_day:
        if current_day in list_of_dates:
            # Get the datetime range for the break on the current day
            break_start_datetime = (
                datetime.datetime.combine(current_day, datetime.time.min)
                + break_start_time
            )
            break_end_datetime = (
                datetime.datetime.combine(current_day, datetime.time.min)
                + break_end_time
            )

            # Check if the datetime range overlaps with the break time
            if (
                start_datetime <= break_end_datetime
                and end_datetime >= break_start_datetime
            ):
                break_count += 1

                # Add 1 hour to the end_datetime
                end_datetime += datetime.timedelta(hours=1)

                # Update the final start and end datetime for output
                # final_start_datetime = start_datetime
                final_end_datetime = end_datetime

        # Prevent counting the same break again on the same day by setting start_datetime to the next day
        # If no break is hit, just move to the next day
        start_datetime = datetime.datetime.combine(
            current_day + datetime.timedelta(days=1), datetime.time.min
        )
        current_day = start_datetime.date()

    # Output the count, and the resulting start and end datetimes
    return break_count, final_start_datetime, final_end_datetime
