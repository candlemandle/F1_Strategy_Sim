from src.strategy import StrategyOptimizer

# Initialize the optimizer
# We are simulating a 57-lap race (like Bahrain)
optimizer = StrategyOptimizer(total_laps=57)

print("--- STARTING OPTIMIZATION ---")
print("Simulating thousands of race strategies...")

# 1. Run the 1-Stop Solver
time_1, strat_1 = optimizer.find_optimal_1_stop()

# 2. Run the 2-Stop Solver
time_2, strat_2 = optimizer.find_optimal_2_stop()

# 3. Compare and Declare a Winner
print("\n--- FINAL VERDICT ---")
if time_1 < time_2:
    diff = (time_2 - time_1) * 60
    print(f"WINNER: 1-Stop Strategy is faster by {diff:.1f} seconds.")
    print(f"Strategy: {strat_1[1]} (Box Lap {strat_1[0]})")
else:
    diff = (time_1 - time_2) * 60
    print(f"WINNER: 2-Stop Strategy is faster by {diff:.1f} seconds.")
    print(f"Strategy: {strat_2[1]} (Box Laps {strat_2[0]})")