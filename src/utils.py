import fastf1
import pandas as pd
import numpy as np
import os

# Enable cache
fastf1.Cache.enable_cache('../data/cache')


def get_race_data(year, gp, session_type='R'):

    # Downloads race data and returns a DataFrame with:
    # Driver, LapNumber, LapTime (sec), Compound, TireLife, Freshman
    print(f"Loading {year} {gp}...")
    session = fastf1.get_session(year, gp, session_type)
    session.load()

    laps = session.laps

    # Select only relevant columns
    # We need 'LapTime', 'TyreLife', 'Compound', 'Driver'
    # Note: FastF1 LapTime is a Timedelta, we need seconds.

    df = laps[['Driver', 'LapNumber', 'LapTime', 'TyreLife', 'Compound', 'Stint']].copy()

    # Drop rows where LapTime is NaT or Safety Car laps
    df = df.dropna(subset=['LapTime'])

    # Convert LapTime to Seconds (float)
    df['LapTimeSec'] = df['LapTime'].dt.total_seconds()

    # Filter out "In Laps" and "Out Laps" (Pit stops)
    # FastF1 marks these effectively, but we can also filter by outlier times
    # A simple way: remove laps > 107% of the median lap time of the race
    median_time = df['LapTimeSec'].median()
    df = df[df['LapTimeSec'] < median_time * 1.07]

    return df


if __name__ == "__main__":
    # Test it
    data = get_race_data(2024, 'Bahrain')
    print(data.head())
    print(f"Total Laps Collected: {len(data)}")

    # Save to CSV for analysis
    os.makedirs('../data/processed', exist_ok=True)
    data.to_csv('../data/processed/2024_Bahrain_Clean.csv', index=False)