import market_data as md
import pandas as pd

def get_target_dates(schedule, weeks_ago):
    s = pd.Series(schedule)
    weeks = s.dt.isocalendar().year.astype(str) + '-' + s.dt.isocalendar().week.astype(str).str.zfill(2)
    unique_weeks = weeks.drop_duplicates().tolist()
    unique_weeks.reverse()
    
    if weeks_ago >= len(unique_weeks):
        return []
        
    target_week = unique_weeks[weeks_ago]
    week_indices = s.index[weeks == target_week].tolist()
    
    if not week_indices:
        return []
        
    start_idx = week_indices[0]
    end_idx = week_indices[-1]
    
    if start_idx > 0:
        start_idx -= 1
        
    return schedule[start_idx:end_idx+1]

schedule = md.get_schedule()
for w in range(3):
    td = get_target_dates(schedule, w)
    print(f"weeks_ago={w}: {len(td)} days, from {td[0].date()} to {td[-1].date()}")
    
