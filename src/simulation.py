import random
import json
import os
import math


class RaceCar:
    def __init__(self, team_name, track_name):
        self.team_name = team_name
        self.track_name = track_name

        # --- PATH FINDING ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        team_db_path = os.path.join(project_root, 'data', 'team_db.json')
        track_db_path = os.path.join(project_root, 'data', 'track_db.json')

        # Load Databases
        try:
            with open(team_db_path, 'r') as f:
                team_db = json.load(f)
            with open(track_db_path, 'r') as f:
                track_db = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Database not found at {team_db_path}")

        # Stats Loading
        if team_name not in team_db:
            print(f"[WARNING] Using Red Bull default for {team_name}")
            self.team_stats = team_db.get('Red Bull Racing', {'pace_index': 1.0, 'deg_index': 1.0})
        else:
            self.team_stats = team_db[team_name]

        self.track_stats = track_db.get(track_name, {'avg_deg': 0.05})

        # --- PHYSICS ENGINE ---
        self.base_lap_time = 90.0 * self.team_stats['pace_index']
        self.current_fuel = 110.0
        self.fuel_burn = 1.7
        self.fuel_penalty = 0.035

        # 1. Degradation Model (The "Haas Effect")
        base_deg = self.track_stats['avg_deg']
        team_factor = self.team_stats['deg_index']

        self.tire_deg_coeffs = {
            'SOFT': base_deg * team_factor,
            'MEDIUM': (base_deg * 0.7) * team_factor,
            'HARD': (base_deg * 0.4) * team_factor
        }

        # 2. Compound Pace Model (NEW!)
        # How much SLOWER is this tire compared to a Soft?
        self.tire_pace_offsets = {
            'SOFT': 0.0,  # Baseline
            'MEDIUM': 0.5,  # +0.5s slower
            'HARD': 1.0  # +1.0s slower (Big penalty!)
        }

        # State
        self.current_tire = 'SOFT'
        self.tire_age = 0
        self.laps_completed = 0
        self.total_race_time = 0.0
        self.history = []

    def pit_stop(self, new_compound):
        pit_loss = 22.0
        self.current_tire = new_compound
        self.tire_age = 0
        self.total_race_time += pit_loss
        if self.history:
            self.history[-1]['Time'] += pit_loss

    def simulate_lap(self):
        # 1. Base Pace
        lap_time = self.base_lap_time

        # 2. Fuel Effect
        lap_time += self.current_fuel * self.fuel_penalty

        # 3. Compound Pace Delta (The Fix)
        # Hards make you slower immediately!
        lap_time += self.tire_pace_offsets.get(self.current_tire, 0.0)

        # 4. Degradation (Linear)
        deg_per_lap = self.tire_deg_coeffs.get(self.current_tire, 0.05)
        lap_time += self.tire_age * deg_per_lap

        # 5. The Cliff (Exponential Decay)
        cliff_alert = 0.0
        if self.current_tire == 'SOFT' and self.tire_age > 18:
            cliff_alert = 0.1 * math.exp(0.3 * (self.tire_age - 18))  # Steeper cliff
        elif self.current_tire == 'MEDIUM' and self.tire_age > 28:
            cliff_alert = 0.1 * math.exp(0.3 * (self.tire_age - 28))

        lap_time += cliff_alert

        # 6. Randomness
        variance = 0.1 * self.team_stats['pace_index']
        lap_time += random.uniform(-variance, variance)

        # Update State
        self.current_fuel -= self.fuel_burn
        self.tire_age += 1
        self.laps_completed += 1
        self.total_race_time += lap_time

        self.history.append({
            'Lap': self.laps_completed,
            'Time': lap_time,
            'Compound': self.current_tire,
            'TyreAge': self.tire_age
        })

        return lap_time