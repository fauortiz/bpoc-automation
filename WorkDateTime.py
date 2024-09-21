# extend the python datetime object. instead of using the full 24 hours as a day, it uses only 9am-6pm.
# keep the implementation as simple as possible. do not allow creating instances outside of 9am-6pm. only implement adding timedelta correctly.

from datetime import datetime, timedelta


class WorkDateTime:
    def __init__(self, list_of_workdays, year, month, day, hour=9, minute=0, second=0):
        # if hour < 9 or hour > 18:
        #     raise ValueError("Hour must be between 9 and 18")
        self.datetime = datetime(year, month, day, hour, minute, second)
        self.list_of_workdays = list_of_workdays

    def __add__(self, delta_arg):
        if not isinstance(delta_arg, timedelta):
            return NotImplemented

        def get_next_workday(dt, list_of_workdays):
            """Helper function to get the start of the next workday."""
            # TODO use list of workdays, from monthly.py
            # SHIT'S BUGGY

            try:
                index_of_next_day = (
                    list_of_workdays.index(dt.date()) + 1
                )  # Find the index of the value
                dt = list_of_workdays[index_of_next_day]
            except IndexError:
                if not index_of_next_day == len(list_of_workdays):
                    raise IndexError

            # print(dt)  # returns 2024-09-03
            # print(type(dt))  # returns <class 'pendulum.date.Date'>
            return datetime(dt.year, dt.month, dt.day, 9, 0, 0)

        def get_end_of_workday(dt):
            """Helper function to get the end of the workday."""
            return dt.replace(hour=18, minute=0, second=0, microsecond=0)

        # initialize data
        current_dt = self.datetime
        remaining_delta = delta_arg
        raw_result = self.datetime + remaining_delta

        # if result is in a future day, get the excess and move it to the next day. if it's still true, do it again. recursive.
        # if same day and the hour is > 18, get the excess and move it to next day.
        # else, it's the same day, within work hours, then break.
        while raw_result.day > current_dt.day or (
            raw_result.day == current_dt.day
            and (
                raw_result.hour > 18
                or (raw_result.hour == 18 and raw_result.minute > 0)
            )
        ):
            # print("raw result > current day")
            # print(f"current_dt: {current_dt}")
            # print(f"raw_result: {raw_result}")
            # print(f"remaining_delta: {remaining_delta}")
            end_of_workday = get_end_of_workday(current_dt)
            remaining_delta = raw_result - end_of_workday
            current_dt = get_next_workday(current_dt, self.list_of_workdays)
            raw_result = current_dt + remaining_delta
            # print("...done!")
            # print(f"current_dt: {current_dt}")
            # print(f"raw_result: {raw_result}")
            # print(f"remaining_delta: {remaining_delta}")

        result = raw_result
        return WorkDateTime(
            self.list_of_workdays,
            result.year,
            result.month,
            result.day,
            result.hour,
            result.minute,
            result.second,
        )

    def __str__(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return (
            f"WorkdayDateTime({self.datetime.year}, {self.datetime.month}, {self.datetime.day}, "
            f"{self.datetime.hour}, {self.datetime.minute}, {self.datetime.second})"
        )

    def adjust_to_next_workday(self):
        """
        Converts the datetime to 9am of the next workday if it's at 6pm of the current workday.
        """
        if self.datetime.hour == 18 and self.datetime.minute == 0:
            next_workday = self.get_next_workday(self.datetime, self.list_of_workdays)
            self.datetime = datetime(
                next_workday.year, next_workday.month, next_workday.day, 9, 0, 0
            )
        return self

    def get_next_workday(self, dt, list_of_workdays):
        """Helper function to get the start of the next workday."""
        try:
            index_of_next_day = list_of_workdays.index(dt.date()) + 1
            return list_of_workdays[index_of_next_day]
        except IndexError:
            if index_of_next_day == len(list_of_workdays):
                # If we've reached the end of the list, we need to handle this case
                # For now, we'll just return the first day of the next month
                # You might want to adjust this logic based on your specific requirements
                next_month = dt.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=1)
            raise IndexError("Unexpected error in get_next_workday")


# # Create an instance of WorkdayDateTime
# workday_now = WorkdayDateTime([], 2024, 9, 11)
# print(f"Current workday time: {workday_now}")

# # Add 1 hour and 30 minutes to the current workday time
# new_time = workday_now + timedelta(hours=1, minutes=30)
# print(f"Time after adding 1 hour and 30 minutes: {new_time}")

# # Add 12 hours (which crosses into non-working hours)
# crossing_hours = workday_now + timedelta(hours=9, minutes=1)
# print(f"Time after adding 9 hours 1 min: {crossing_hours}")

# # Add 12 hours (which crosses into the next workday)
# crossing_days = workday_now + timedelta(hours=19)
# print(f"Time after adding 19 hours: (Expect sept 13, 10am) {crossing_days}")
