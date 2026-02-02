import os
from src.utils import get_race_data

# We will grab the 2023 season because it's a complete dataset with consistent car performance.
RACES_2023 = [
    'Bahrain', 'Saudi Arabia', 'Australia', 'Azerbaijan', 'Miami',
    'Monaco', 'Spain', 'Canada', 'Austria', 'Great Britain',
    'Hungary', 'Belgium', 'Netherlands', 'Italy', 'Singapore',
    'Japan', 'Qatar', 'United States', 'Mexico', 'Brazil', 'Las Vegas', 'Abu Dhabi'
]


def mine_season_data(year=2023):
    print(f"--- STARTING DATA MINING FOR {year} ---")
    save_dir = f'../data/season_{year}'
    os.makedirs(save_dir, exist_ok=True)

    for gp in RACES_2023:
        file_path = f'{save_dir}/{gp}_Clean.csv'

        if os.path.exists(file_path):
            print(f"[SKIP] {gp} already exists.")
            continue

        print(f"[DOWNLOADING] {gp}...")
        df = get_race_data(year, gp)

        if not df.empty:
            df.to_csv(file_path, index=False)
            print(f"[SUCCESS] Saved {len(df)} laps for {gp}")
        else:
            print(f"[WARNING] No data found for {gp}")


if __name__ == "__main__":
    mine_season_data(2023)