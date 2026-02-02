from src.simulation import RaceCar
import copy


class StrategyOptimizer:
    def __init__(self, total_laps=57):
        self.total_laps = total_laps
        # We assume standard Bahrain tire degradation
        self.coeffs = {'SOFT': 0.045, 'MEDIUM': 0.038, 'HARD': 0.030}

    def evaluate_strategy(self, stop_laps, compounds):

        # Create a fresh car for this simulation
        car = RaceCar(tire_deg_coeffs=self.coeffs)

        # We need an iterator for compounds: Start on compounds[0], then switch to [1], etc.
        current_compound_idx = 0
        car.current_tire = compounds[0]  # Start tire

        # Convert stop_laps to a set for fast lookup
        stops_set = set(stop_laps)

        for lap in range(1, self.total_laps + 1):
            # Check if this lap is a pit stop
            if lap in stops_set:
                current_compound_idx += 1
                if current_compound_idx < len(compounds):
                    next_tire = compounds[current_compound_idx]
                    car.pit_stop(next_tire)

            car.simulate_lap()

        return car.total_race_time / 60.0  # Return in minutes

    def find_optimal_1_stop(self):
        print("--- Optimizing 1-Stop Strategy ---")
        best_time = float('inf')
        best_strategy = None

        # Try stopping on every lap from 10 to 50
        # Try every tire combo: S-H, S-M, M-H
        tire_combos = [
            ['SOFT', 'HARD'],
            ['SOFT', 'MEDIUM'],
            ['MEDIUM', 'HARD']
        ]

        for lap in range(10, 50):
            for combo in tire_combos:
                time = self.evaluate_strategy([lap], combo)

                if time < best_time:
                    best_time = time
                    best_strategy = (lap, combo)

        print(f"BEST 1-STOP: Box Lap {best_strategy[0]} | Tires: {best_strategy[1]} | Time: {best_time:.2f} min")
        return best_time, best_strategy

    def find_optimal_2_stop(self):
        print("\n--- Optimizing 2-Stop Strategy ---")
        best_time = float('inf')
        best_strategy = None

        # Try all combinations of two stops.
        # This loop runs roughly 50*50 = 2500 times. Very fast for a computer.
        tire_combos = [
            ['SOFT', 'HARD', 'SOFT'],
            ['SOFT', 'MEDIUM', 'SOFT'],
            ['SOFT', 'HARD', 'MEDIUM']
        ]

        for stop1 in range(10, 40):
            for stop2 in range(stop1 + 10, 52):  # Ensure 2nd stop is at least 10 laps later
                for combo in tire_combos:
                    time = self.evaluate_strategy([stop1, stop2], combo)

                    if time < best_time:
                        best_time = time
                        best_strategy = ([stop1, stop2], combo)

        print(f"BEST 2-STOP: Box Laps {best_strategy[0]} | Tires: {best_strategy[1]} | Time: {best_time:.2f} min")
        return best_time, best_strategy