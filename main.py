from src.strategy import StrategyOptimizer

# We test with FERRARI because they have average tire wear (good benchmark)
optimizer = StrategyOptimizer(team="Ferrari", track="Bahrain", total_laps=57)

print("--- STARTING STRATEGY OPTIMIZATION (WITH TIRE CLIFF) ---")

# 1. Run Solvers
time_1, strat_1 = optimizer.find_optimal_1_stop()
print(f"Best 1-Stop: {time_1:.2f} min | Box: {strat_1[0]} | Tires: {strat_1[1]}")

time_2, strat_2 = optimizer.find_optimal_2_stop()
print(f"Best 2-Stop: {time_2:.2f} min | Box: {strat_2[0]} | Tires: {strat_2[1]}")

# 2. Verdict
print("\n--- FINAL VERDICT ---")
if time_1 < time_2:
    print(f"WINNER: 1-Stop is faster by {(time_2 - time_1)*60:.2f} sec.")
else:
    print(f"WINNER: 2-Stop is faster by {(time_1 - time_2)*60:.2f} sec.")