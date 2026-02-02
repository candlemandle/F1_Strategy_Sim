# 0. Testing the libraries and enviroment
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# 1. Setup the Cache
fastf1.Cache.enable_cache('../data/cache')

# 2. Load the Session
print("Loading 2024 Bahrain Grand Prix data...")
race = fastf1.get_session(2024, 'Bahrain', 'R')
race.load()

# 3. Get Data for the Winner (Max Verstappen aka the GOAT)
ver_laps = race.laps.pick_driver('VER')

# 4. Filter for "clean" laps (no pit in/out laps)
clean_laps = ver_laps.pick_quicklaps()

# 5. Plot Lap Times (The start of your research!)
print("Plotting data...")
fig, ax = plt.subplots()
ax.plot(clean_laps['LapNumber'], clean_laps['LapTime'], label='VER Lap Times')
ax.set_xlabel('Lap Number')
ax.set_ylabel('Lap Time')
ax.set_title('Verstappen Lap Times - Bahrain 2024')
plt.show()