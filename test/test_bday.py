import market_data as md
from datetime import datetime, timedelta
import pytz
import unittest
from pandas_market_calendars import get_calendar

nyse = get_calendar("NYSE")


def get_schedule():
    today = datetime.now(pytz.timezone("America/New_York")).date()
    schedule = nyse.valid_days(
        start_date=today - timedelta(days=370),
        end_date=today,
    )
    return schedule


def get_business_days(schedule):
    to_date = schedule[-1].date()
    one_year_ago = to_date.replace(year=to_date.year - 1)
    from_date = max(d.date() for d in schedule if d.date() <= one_year_ago)

    business_days = [d.date() for d in reversed(schedule) if from_date <= d.date() <= to_date]
    return business_days


schedule = get_schedule()
business_days = get_business_days(schedule)

start_date = business_days[6]
end_date = business_days[1]

test_bdays = [d for d in reversed(business_days) if start_date <= d <= end_date]
print(test_bdays)
# Format each date as string
formatted_dates = [d.strftime('%Y-%m-%d') for d in test_bdays]
print(formatted_dates)

# Or print directly in the f-string
print(f"Business days: {[d.strftime('%Y-%m-%d') for d in test_bdays]}")

#expected_dates = pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"])

print(f"Business days from {start_date} to {end_date}: {len(test_bdays)}")
print(f"Business days: {test_bdays}")
print(f"Total: {len(business_days)}")
