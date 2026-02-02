from src.simulation import RaceCar


class StrategyOptimizer:
    def __init__(self, team="Red Bull Racing", track="Bahrain", total_laps=57):
        self.team = team
        self.track = track
        self.total_laps = total_laps

    def evaluate_strategy(self, stop_laps, compounds):
        # Create the car with REAL data
        car = RaceCar(team_name=self.team, track_name=self.track)

        current_compound_idx = 0
        car.current_tire = compounds[0]  # Start tire

        stops_set = set(stop_laps)

        for lap in range(1, self.total_laps + 1):
            if lap in stops_set:
                current_compound_idx += 1
                if current_compound_idx < len(compounds):
                    next_tire = compounds[current_compound_idx]
                    car.pit_stop(next_tire)

            car.simulate_lap()

        return car.total_race_time / 60.0  # Return in minutes

    def find_optimal_1_stop(self):
        print(f"--- Optimizing 1-Stop ({self.team} @ {self.track}) ---")
        best_time = float('inf')
        best_strategy = None

        tire_combos = [['SOFT', 'HARD'], ['SOFT', 'MEDIUM'], ['MEDIUM', 'HARD']]

        # Search pit window: Lap 15 to 45
        for lap in range(15, 45):
            for combo in tire_combos:
                time = self.evaluate_strategy([lap], combo)
                if time < best_time:
                    best_time = time
                    best_strategy = (lap, combo)

        return best_time, best_strategy

    def find_optimal_2_stop(self):
        print(f"--- Optimizing 2-Stop ({self.team} @ {self.track}) ---")
        best_time = float('inf')
        best_strategy = None

        tire_combos = [
            ['SOFT', 'HARD', 'SOFT'],
            ['SOFT', 'MEDIUM', 'SOFT'],
            ['SOFT', 'HARD', 'MEDIUM']
        ]

        # Search pit windows
        for stop1 in range(12, 30):
            for stop2 in range(stop1 + 15, 50):
                for combo in tire_combos:
                    time = self.evaluate_strategy([stop1, stop2], combo)
                    if time < best_time:
                        best_time = time
                        best_strategy = ([stop1, stop2], combo)

        return best_time, best_strategy