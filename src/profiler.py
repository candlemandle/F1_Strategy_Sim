import pandas as pd
import numpy as np
import os
import json
from sklearn.linear_model import LinearRegression

DATA_DIR = '../data/season_2023'


def profile_season():
    print("--- STARTING SEASON PROFILING ---")

    # 1. Initialize Databases
    track_db = {}
    team_stats = {}  # { 'Red Bull': {'pace_deficits': [], 'deg_factors': []} }

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    for file in files:
        gp_name = file.replace('_Clean.csv', '')
        print(f"Analyzing {gp_name}...")

        try:
            df = pd.read_csv(os.path.join(DATA_DIR, file))
        except Exception as e:
            print(f"Skipping {gp_name} (Read Error)")
            continue

        # --- FIX: SANITIZE DATA IMMEDIATELY ---
        # Remove any rows where TyreLife or LapTimeSec is missing (NaN)
        df = df.dropna(subset=['TyreLife', 'LapTimeSec'])

        # --- Physics Correction ---
        # We assume Fuel Correction = 0.05s/lap generic
        df['FuelCorrectedTime'] = df['LapTimeSec'] + (df['LapNumber'] * 0.05)

        # --- A. TRACK PROFILING ---
        # We want the "Average Degradation" of this track (across all cars)
        # We filter for 'clean' racing laps (no pit out/in)

        # Determine Track Baseline
        track_deg = 0.045  # Default fallback
        valid_laps = df[df['TyreLife'] < 30]  # focus on the "linear" phase

        if len(valid_laps) > 100:
            X = valid_laps[['TyreLife']].values
            y = valid_laps['FuelCorrectedTime'].values

            # Sanity Check for NaNs again just in case
            if not np.isnan(X).any() and not np.isnan(y).any():
                reg = LinearRegression().fit(X, y)
                track_deg = max(0.01, float(reg.coef_[0]))  # Ensure positive and non-zero

        track_db[gp_name] = {
            'avg_deg': track_deg,
            'laps': int(df['LapNumber'].max())
        }

        # --- B. TEAM PROFILING ---
        # 1. Who was the fastest team this race? (Baseline)
        team_medians = df.groupby('Team')['LapTimeSec'].median()
        if team_medians.empty: continue

        fastest_time = team_medians.min()

        teams = df['Team'].unique()
        for team in teams:
            team_laps = df[df['Team'] == team]

            # Clean team data specifically
            team_laps = team_laps.dropna(subset=['TyreLife', 'FuelCorrectedTime'])

            if len(team_laps) < 10: continue

            # Pace Metric: How much slower than the winner? (1.00 = Equal, 1.01 = 1% slower)
            my_median = team_laps['LapTimeSec'].median()
            pace_deficit = my_median / fastest_time

            # Deg Metric: Does this team degrade faster than the Track Average?
            my_deg = track_deg  # Default to average

            if len(team_laps) > 20:
                X_team = team_laps[['TyreLife']].values
                y_team = team_laps['FuelCorrectedTime'].values

                if not np.isnan(X_team).any():
                    reg_team = LinearRegression().fit(X_team, y_team)
                    my_deg = float(reg_team.coef_[0])

            # Deg Factor: 1.0 = Average, 1.2 = High Wear
            deg_factor = my_deg / track_deg

            # Cap extreme outliers (sometimes bad data makes deg factor 5.0 or -2.0)
            deg_factor = max(0.5, min(2.0, deg_factor))

            if team not in team_stats:
                team_stats[team] = {'pace_deficits': [], 'deg_factors': []}

            team_stats[team]['pace_deficits'].append(pace_deficit)
            team_stats[team]['deg_factors'].append(deg_factor)

    # --- C. AGGREGATE RESULTS ---
    print("\n--- TEAM PERFORMANCE INDEX (2023) ---")
    final_team_db = {}

    for team, stats in team_stats.items():
        avg_pace = np.mean(stats['pace_deficits'])
        avg_deg = np.mean(stats['deg_factors'])

        final_team_db[team] = {
            'pace_index': round(avg_pace, 4),
            'deg_index': round(avg_deg, 3)
        }
        print(f"{team:<25} | Pace: {avg_pace:.4f} | Deg: {avg_deg:.2f}")

    # Save to JSON
    with open('../data/track_db.json', 'w') as f:
        json.dump(track_db, f, indent=4)

    with open('../data/team_db.json', 'w') as f:
        json.dump(final_team_db, f, indent=4)

    print("\n[SUCCESS] Databases saved to /data/")


if __name__ == "__main__":
    profile_season()