import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.simulation import RaceCar
from src.strategy import StrategyOptimizer
import threading

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class F1SimApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("F1 Strategy Optimizer - Diploma Project")
        self.geometry("1200x800")

        # --- LAYOUT CONFIG ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR (Controls) ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="STRATEGY\nENGINEER", font=("Arial", 24, "bold"))
        self.logo_label.pack(pady=30)

        # Team Selection
        ctk.CTkLabel(self.sidebar, text="Select Team:", anchor="w").pack(fill="x", padx=20, pady=(10, 0))
        self.team_menu = ctk.CTkOptionMenu(self.sidebar, values=[
            "Red Bull Racing", "Ferrari", "Mercedes", "McLaren",
            "Aston Martin", "Alpine", "Williams", "Haas F1 Team"
        ])
        self.team_menu.pack(fill="x", padx=20, pady=5)

        # Track Selection
        ctk.CTkLabel(self.sidebar, text="Select Track:", anchor="w").pack(fill="x", padx=20, pady=(20, 0))
        self.track_menu = ctk.CTkOptionMenu(self.sidebar, values=[
            "Bahrain", "Saudi Arabia", "Australia", "Monaco",
            "Spain", "Canada", "Monza", "Las Vegas"
        ])
        self.track_menu.pack(fill="x", padx=20, pady=5)

        # Rain Probability
        ctk.CTkLabel(self.sidebar, text="Rain Probability (%):", anchor="w").pack(fill="x", padx=20, pady=(20, 0))
        self.rain_slider = ctk.CTkSlider(self.sidebar, from_=0, to=100, number_of_steps=100)
        self.rain_slider.set(0)
        self.rain_slider.pack(fill="x", padx=20, pady=5)

        # Run Button
        self.run_btn = ctk.CTkButton(self.sidebar, text="RUN SIMULATION", height=50,
                                     fg_color="#E10600", hover_color="#8a0400",  # F1 Red
                                     font=("Arial", 16, "bold"),
                                     command=self.start_simulation_thread)
        self.run_btn.pack(fill="x", padx=20, pady=40)

        # Console Log
        self.textbox = ctk.CTkTextbox(self.sidebar, height=200)
        self.textbox.pack(fill="x", padx=20, pady=10)
        self.textbox.insert("0.0", "System Ready.\nSelect parameters and click Run.\n")

        # --- RIGHT SIDE (Visualization) ---
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.current_canvas = None

    def log(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")

    def start_simulation_thread(self):
        # Run simulation in background so GUI doesn't freeze
        self.run_btn.configure(state="disabled", text="CALCULATING...")
        threading.Thread(target=self.run_simulation).start()

    def run_simulation(self):
        team = self.team_menu.get()
        track = self.track_menu.get()
        rain = int(self.rain_slider.get())

        self.log(f"\n>>> NEW SESSION: {team} @ {track}")
        self.log(f"Conditions: {rain}% Rain Probability")

        try:
            # 1. Initialize Optimizer
            optimizer = StrategyOptimizer(team=team, track=track, rain_prob=rain)

            # 2. Find Strategies
            t1, s1 = optimizer.find_optimal_1_stop()
            self.log(f"1-Stop Best: {t1:.2f}m (Box: {s1[0]})")

            t2, s2 = optimizer.find_optimal_2_stop()
            self.log(f"2-Stop Best: {t2:.2f}m (Box: {s2[0]})")

            # 3. Determine Winner
            if t2 < t1:
                self.log(f"RECOMMENDATION: 2-STOP (-{(t1 - t2) * 60:.1f}s)")
            else:
                self.log(f"RECOMMENDATION: 1-STOP (-{(t2 - t1) * 60:.1f}s)")

            # 4. Plot (Must be done on main thread usually, but Matplotlib/Tk handles it ok here)
            self.plot_results(team, track, rain, s1, s2)

        except Exception as e:
            self.log(f"ERROR: {e}")

        self.run_btn.configure(state="normal", text="RUN SIMULATION")

    def plot_results(self, team, track, rain, strat1, strat2):
        # Clear old graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Re-Simulate the best laps for plotting
        car1 = self.run_single_race(team, track, rain, strat1)
        car2 = self.run_single_race(team, track, rain, strat2)

        # Matplotlib Figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        laps = range(1, 58)
        times1 = [x['Time'] for x in car1.history]
        times2 = [x['Time'] for x in car2.history]

        ax.plot(laps, times1, label=f'1-Stop ({strat1[1]})', color='cyan', linewidth=2)
        ax.plot(laps, times2, label=f'2-Stop ({strat2[1]})', color='orange', linewidth=2)

        ax.set_title(f"Race Pace Strategy Analysis\n{team} | {track}", color='white', fontsize=14)
        ax.set_xlabel("Lap Number", color='white')
        ax.set_ylabel("Lap Time (s)", color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, color='#444444', linestyle='--')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def run_single_race(self, team, track, rain, strategy):
        car = RaceCar(team, track, rain)
        car.current_tire = strategy[1][0]
        stops = strategy[0] if isinstance(strategy[0], list) else [strategy[0]]
        tires = strategy[1]
        t_idx = 0

        for lap in range(1, 58):
            if lap in stops:
                t_idx += 1
                if t_idx < len(tires):
                    car.pit_stop(tires[t_idx])
            car.simulate_lap()
        return car


if __name__ == "__main__":
    app = F1SimApp()
    app.mainloop()