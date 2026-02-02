import fastf1
import pandas as pd
import numpy as np

# Enable cache
fastf1.Cache.enable_cache('../data/cache')


def get_race_data(year, gp, session_type='R'):
    print(f"Loading {year} {gp}...")
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
    except Exception as e:
        print(f"Error loading session: {e}")
        return pd.DataFrame()  # Return empty if fails

    laps = session.laps

    # --- FIX: We added 'Team' to this list ---
    # We also keep 'Driver' so we can track teammates
    columns_we_need = ['Driver', 'Team', 'LapNumber', 'LapTime', 'TyreLife', 'Compound', 'Stint']

    # Check if columns exist before selecting
    available_cols = [c for c in columns_we_need if c in laps.columns]
    df = laps[available_cols].copy()

    # Drop rows where LapTime is missing
    df = df.dropna(subset=['LapTime'])

    # Convert LapTime to Seconds
    df['LapTimeSec'] = df['LapTime'].dt.total_seconds()

    # Filter outliers (107% rule)
    median_time = df['LapTimeSec'].median()
    df = df[df['LapTimeSec'] < median_time * 1.07]

    return df