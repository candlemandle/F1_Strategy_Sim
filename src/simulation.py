import random
import json
import os
import math


class RaceCar:
    def __init__(self, team_name, track_name, rain_prob=0):
        self.team_name = team_name
        self.track_name = track_name
        self.rain_prob = rain_prob
        self.is_raining = False

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
            # Fallback
            self.team_stats = team_db.get('Red Bull Racing', {'pace_index': 1.0, 'deg_index': 1.0})
        else:
            self.team_stats = team_db[team_name]

        self.track_stats = track_db.get(track_name, {'avg_deg': 0.05})

        # --- PHYSICS ENGINE ---
        self.base_lap_time = 90.0 * self.team_stats['pace_index']
        self.current_fuel = 110.0
        self.fuel_burn = 1.7
        self.fuel_penalty = 0.035

        # Degradation & Pace
        base_deg = self.track_stats['avg_deg']
        team_factor = self.team_stats['deg_index']

        self.tire_deg_coeffs = {
            'SOFT': base_deg * team_factor,
            'MEDIUM': (base_deg * 0.7) * team_factor,
            'HARD': (base_deg * 0.4) * team_factor,
            'INTER': 0.02
        }

        self.tire_pace_offsets = {
            'SOFT': 0.0,
            'MEDIUM': 0.5,
            'HARD': 1.0,
            'INTER': 5.0
        }

        self.current_tire = 'SOFT'
        self.tire_age = 0
        self.laps_completed = 0
        self.total_race_time = 0.0
        self.history = []

        # --- THIS WAS MISSING OR BROKEN ---

    def pit_stop(self, new_compound, reason="Scheduled"):
        # Reduced cost under Safety Car
        # Check previous lap history for SC status
        is_sc = False
        if self.history:
            is_sc = self.history[-1].get('SC', False)

        pit_loss = 12.0 if is_sc else 22.0

        self.current_tire = new_compound
        self.tire_age = 0
        self.total_race_time += pit_loss

        # Record the reasoning for the GUI
        if self.history:
            self.history[-1]['Time'] += pit_loss
            self.history[-1]['PitStop'] = True
            self.history[-1]['PitReason'] = reason

    def check_weather(self):
        if self.rain_prob == 0: return

        roll = random.uniform(0, 100)
        if self.is_raining:
            if roll < 5:
                self.is_raining = False
        else:
            chance = self.rain_prob / 10.0
            if roll < chance:
                self.is_raining = True

    def simulate_lap(self):
        # 0. Weather & SC Checks
        self.check_weather()

        # Safety Car Probability (Higher on street tracks)
        sc_chance = 2.0 if self.track_name in ["Monaco", "Azerbaijan", "Singapore"] else 0.5
        is_safety_car = random.uniform(0, 100) < sc_chance

        # 1. Base Pace
        lap_time = self.base_lap_time
        lap_time += self.current_fuel * self.fuel_penalty
        lap_time += self.tire_pace_offsets.get(self.current_tire, 0.0)

        # 2. Weather Physics
        if self.is_raining:
            if self.current_tire == 'INTER':
                lap_time += 10.0
            else:
                lap_time += 30.0
        else:
            if self.current_tire == 'INTER':
                lap_time += 5.0

                # 3. Safety Car Physics
        if is_safety_car:
            lap_time += 40.0  # Slow delta

        # 4. Degradation
        deg_factor = 0.2 if is_safety_car else 1.0
        deg_per_lap = self.tire_deg_coeffs.get(self.current_tire, 0.05)
        lap_time += (self.tire_age * deg_per_lap) * deg_factor

        # 5. Cliff
        cliff_alert = 0.0
        if not is_safety_car:
            if self.current_tire == 'SOFT' and self.tire_age > 18:
                cliff_alert = 0.1 * math.exp(0.3 * (self.tire_age - 18))
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
            'TyreAge': self.tire_age,
            'Rain': self.is_raining,
            'SC': is_safety_car
        })

        return lap_time