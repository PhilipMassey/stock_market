import market_data as md
import pandas as pd

schedule = md.get_schedule()
# Group by ISO year and week
s = pd.Series(schedule)
# Create a unique week identifier
weeks = s.dt.isocalendar().year.astype(str) + '-' + s.dt.isocalendar().week.astype(str).str.zfill(2)

# Get unique weeks preserving order
unique_weeks = weeks.drop_duplicates().tolist()
unique_weeks.reverse()

for weeks_ago in range(3):
    target_week = unique_weeks[weeks_ago]
    week_dates = s[weeks == target_week]
    print(f"weeks_ago={weeks_ago}, week={target_week}: {week_dates.iloc[0].date()} to {week_dates.iloc[-1].date()}")
