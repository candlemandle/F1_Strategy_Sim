import pandas as pd
import sklearn
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# CONSTANTS (We assume these based on F1 physics literature)
# Fuel correction: Cars gain approx 0.05s per lap due to fuel burn (weight loss)
FUEL_CORRECTION_PER_LAP = 0.05


def analyze_tire_wear(file_path):
    print(f"Analyzing {file_path}...")
    df = pd.read_csv(file_path)

    # 1. Calculate 'Fuel Corrected LapTime'
    # We ADD time back to simulate what the lap would be if fuel weight stayed constant.
    # This reveals the TRUE degradation of the tire.
    df['FuelCorrectedTime'] = df['LapTimeSec'] + (df['LapNumber'] * FUEL_CORRECTION_PER_LAP)

    # 2. Analyze per Compound
    compounds = df['Compound'].unique()

    results = {}

    plt.figure(figsize=(10, 6))

    for compound in compounds:
        if pd.isna(compound): continue

        # Get data for this compound
        subset = df[df['Compound'] == compound]

        # Filter outliers (remove very slow laps, e.g., traffic/mistakes)
        # We assume valid laps are within 3 seconds of the driver's best on that tire
        subset = subset[subset['FuelCorrectedTime'] < subset['FuelCorrectedTime'].min() + 3.0]

        if len(subset) < 20:
            print(f"Skipping {compound} (not enough data: {len(subset)} laps)")
            continue

        # Linear Regression: TyreLife (X) vs FuelCorrectedTime (Y)
        X = subset[['TyreLife']].values
        y = subset['FuelCorrectedTime'].values

        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]  # This is the DEGRADATION (sec/lap)
        intercept = model.intercept_  # This is the Base Pace

        results[compound] = slope
        print(f"Compound: {compound} | Degradation: +{slope:.4f} sec/lap")

        # Plot the regression line
        x_range = np.linspace(subset['TyreLife'].min(), subset['TyreLife'].max(), 100).reshape(-1, 1)
        y_pred = model.predict(x_range)
        plt.scatter(subset['TyreLife'], subset['FuelCorrectedTime'], alpha=0.3, label=f'{compound} Raw')
        plt.plot(x_range, y_pred, linewidth=2, label=f'{compound} Trend (+{slope:.3f} s/lap)')

    plt.xlabel('Tire Age (Laps)')
    plt.ylabel('Fuel-Corrected Lap Time (s)')
    plt.title('Tire Degradation Model (Fuel Effect Removed)')
    plt.legend()
    plt.grid(True)
    plt.savefig('../data/processed/tire_degradation_plot.png')
    plt.show()

    return results


if __name__ == "__main__":
    # Point this to the file just created
    coefficients = analyze_tire_wear('../data/processed/2024_Bahrain_Clean.csv')
    print("\n--- FINAL MODEL COEFFICIENTS ---")
    print(coefficients)