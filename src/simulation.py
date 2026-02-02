import random
import numpy as np


class RaceCar:
    def __init__(self, base_lap_time=92.0, fuel_load=110.0, tire_deg_coeffs=None):

        self.base_lap_time = base_lap_time
        self.current_fuel = fuel_load
        self.max_fuel = 110.0

        # Physics Constants
        self.fuel_burn_per_lap = 1.7  # kg/lap
        self.fuel_time_penalty = 0.035  # sec lost per kg of fuel

        # Tire Physics (Default values if none provided)
        if tire_deg_coeffs is None:
            self.tire_deg_coeffs = {
                'SOFT': 0.05,
                'MEDIUM': 0.04,
                'HARD': 0.03
            }
        else:
            self.tire_deg_coeffs = tire_deg_coeffs

        # Car State
        self.current_tire = 'SOFT'
        self.tire_age = 0
        self.laps_completed = 0
        self.total_race_time = 0.0
        self.history = []  # To store lap-by-lap data for plotting

    def pit_stop(self, new_compound):

        pit_loss = 22.0  # Average pit lane loss in Bahrain (sec)

        # Log the event
        print(f"LAP {self.laps_completed}: BOX BOX! Switching {self.current_tire} -> {new_compound}")

        self.current_tire = new_compound
        self.tire_age = 0
        self.total_race_time += pit_loss

        # Record the pit stop in history (as a 'slow' lap)
        self.history[-1]['Time'] += pit_loss

    def simulate_lap(self):

        # 1. Base Pace
        lap_time = self.base_lap_time

        # 2. Add Fuel Penalty (Heavy cars are slower)
        fuel_penalty = self.current_fuel * self.fuel_time_penalty
        lap_time += fuel_penalty

        # 3. Add Tire Degradation
        # Get deg coefficient for current tire, default to 0.05 if unknown
        deg_per_lap = self.tire_deg_coeffs.get(self.current_tire, 0.05)
        tire_penalty = self.tire_age * deg_per_lap
        lap_time += tire_penalty

        # 4. Add Randomness (Driver error, wind, minor variations)
        # Random variance between -0.1s and +0.3s
        random_var = random.uniform(-0.1, 0.3)
        lap_time += random_var

        # Update State
        self.current_fuel -= self.fuel_burn_per_lap
        self.tire_age += 1
        self.laps_completed += 1
        self.total_race_time += lap_time

        # Store Data
        self.history.append({
            'Lap': self.laps_completed,
            'Time': lap_time,
            'Compound': self.current_tire,
            'Fuel': self.current_fuel,
            'TyreAge': self.tire_age
        })

        return lap_time