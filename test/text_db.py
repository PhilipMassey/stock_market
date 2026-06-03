import market_data as md

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas_market_calendars as mcal

nyse = mcal.get_calendar("NYSE")


def get_business_days(start_date: str, end_date: str) -> pd.DatetimeIndex:
    """
    Returns a list of business days between two dates.
    """
    return pd.bdate_range(start=start_date, end=end_date)

if __name__ == "__main__":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=12)  # Go back a bit to ensure we get 5 business days
    business_days = get_business_days(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    print(business_days)
