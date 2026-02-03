import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import os
import json
import threading
from src.simulation import RaceCar
from src.strategy import StrategyOptimizer

# --- VISUAL CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#1e1e1e"
COLOR_ACCENT = "#E10600"  # F1 Red
COLOR_TEXT_DIM = "#aaaaaa"

# Graph Colors (High Contrast)
COLOR_1_STOP = "#00FFFF"  # Cyan
COLOR_2_STOP = "#FF3399"  # Neon Pink/Red
COLOR_SC = "#FFFF00"  # Yellow


class F1SimApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("F1 STRATEGY SIMULATOR 2026")
        self.geometry("1400x900")
        self.configure(fg_color=COLOR_BG)

        # Load Data Sorted
        self.teams_list = sorted(self.load_json_keys('team_db.json', ["Red Bull Racing", "Ferrari"]))
        self.tracks_list = sorted(self.load_json_keys('track_db.json', ["Bahrain", "Monza"]))

        self.setup_ui()

    def setup_ui(self):
        # --- LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#151515")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="RACE CONTROL", font=("DIN Alternate", 24, "bold"), text_color="white").pack(
            pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text="v2.5.0 | DATA-DRIVEN", font=("Arial", 10), text_color=COLOR_TEXT_DIM).pack(
            pady=(0, 30))

        self.create_label("CONSTRUCTOR")
        self.team_menu = ctk.CTkOptionMenu(self.sidebar, values=self.teams_list, fg_color="#333", button_color="#444")
        self.team_menu.pack(fill="x", padx=20, pady=5)

        self.create_label("CIRCUIT")
        self.track_menu = ctk.CTkOptionMenu(self.sidebar, values=self.tracks_list, fg_color="#333", button_color="#444",
                                            command=self.load_track_map)
        self.track_menu.pack(fill="x", padx=20, pady=5)

        self.create_label("METEOROLOGY")
        self.rain_val_label = ctk.CTkLabel(self.sidebar, text="0% CHANCE", text_color=COLOR_ACCENT,
                                           font=("Arial", 12, "bold"))
        self.rain_val_label.pack(anchor="e", padx=20)
        self.rain_slider = ctk.CTkSlider(self.sidebar, from_=0, to=100, number_of_steps=100,
                                         progress_color=COLOR_ACCENT, command=self.update_rain_text)
        self.rain_slider.set(0)
        self.rain_slider.pack(fill="x", padx=20, pady=5)

        self.create_label("SAFETY CAR RISK")
        self.sc_slider = ctk.CTkSlider(self.sidebar, from_=0, to=20, number_of_steps=20, progress_color="orange")
        self.sc_slider.set(2)
        self.sc_slider.pack(fill="x", padx=20, pady=5)

        self.run_btn = ctk.CTkButton(self.sidebar, text="INITIATE STRATEGY", height=50,
                                     fg_color=COLOR_ACCENT, hover_color="#b30500",
                                     font=("DIN Alternate", 16, "bold"),
                                     corner_radius=4,
                                     command=self.start_simulation_thread)
        self.run_btn.pack(side="bottom", fill="x", padx=20, pady=40)

        # ================= CENTER PANEL =================
        self.center_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.graph_frame = ctk.CTkFrame(self.center_panel, fg_color="#2b2b2b", corner_radius=10)
        self.graph_frame.pack(fill="both", expand=True)
        self.current_canvas = None

        self.verdict_frame = ctk.CTkFrame(self.center_panel, height=100, fg_color="#2b2b2b", corner_radius=10)
        self.verdict_frame.pack(fill="x", pady=(20, 0))
        self.verdict_label = ctk.CTkLabel(self.verdict_frame, text="AWAITING DATA...", font=("Arial", 20, "bold"))
        self.verdict_label.place(relx=0.5, rely=0.5, anchor="center")

        # ================= RIGHT PANEL =================
        self.right_panel = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#1a1a1a")
        self.right_panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="TRACK INTEL", font=("DIN Alternate", 18, "bold")).pack(pady=20)
        self.map_label = ctk.CTkLabel(self.right_panel, text="[NO MAP DATA]", width=250, height=150, fg_color="#111",
                                      corner_radius=8)
        self.map_label.pack(pady=10)

        ctk.CTkLabel(self.right_panel, text="LIVE TIMING LOG", font=("DIN Alternate", 14, "bold"), anchor="w").pack(
            fill="x", padx=15, pady=(30, 5))
        self.log_box = ctk.CTkTextbox(self.right_panel, height=400, fg_color="#111", text_color="#00ff00",
                                      font=("Consolas", 12))
        self.log_box.pack(fill="x", padx=15, pady=5)

        self.load_track_map(self.track_menu.get())

    # --- HELPERS ---
    def create_label(self, text):
        ctk.CTkLabel(self.sidebar, text=text, font=("Arial", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w",
                                                                                                          padx=20,
                                                                                                          pady=(20, 5))

    def update_rain_text(self, value):
        self.rain_val_label.configure(text=f"{int(value)}% CHANCE")

    def load_json_keys(self, filename, default_list):
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data', filename)
            with open(path, 'r') as f:
                return json.load(f).keys()
        except:
            return default_list

    def load_track_map(self, track_name):
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tracks')
        filenames = [f"{track_name}.png", f"{track_name.replace(' ', '_')}.png", f"{track_name}.jpg"]
        found = False
        for fname in filenames:
            full_path = os.path.join(base_path, fname)
            if os.path.exists(full_path):
                try:
                    img = ctk.CTkImage(Image.open(full_path), size=(250, 150))
                    self.map_label.configure(image=img, text="")
                    found = True
                    break
                except:
                    pass
        if not found: self.map_label.configure(image=None, text=f"NO MAP FOR\n{track_name.upper()}")

    def log_msg(self, msg, color=None):
        tag = "white"
        if "BOX" in msg: tag = "yellow"
        if "SAFETY" in msg: tag = "red"
        if "RAIN" in msg: tag = "blue"

        self.log_box.insert("end", f">> {msg}\n", tag)
        self.log_box.see("end")

    # --- SIMULATION ---
    def start_simulation_thread(self):
        self.run_btn.configure(state="disabled", text="CALCULATING...", fg_color="#555")
        self.log_box.delete("0.0", "end")
        threading.Thread(target=self.run_process).start()

    def run_process(self):
        team = self.team_menu.get()
        track = self.track_menu.get()
        rain = int(self.rain_slider.get())

        self.log_msg(f"INIT SIM: {team}")
        self.log_msg(f"TRACK: {track}")

        try:
            optimizer = StrategyOptimizer(team=team, track=track, rain_prob=rain)
            t1, s1 = optimizer.find_optimal_1_stop()
            t2, s2 = optimizer.find_optimal_2_stop()

            if t2 < t1:
                winner_strat = s2
                win_text = "2-STOP STRATEGY"
                diff = (t1 - t2) * 60
                detail = f"Faster by {diff:.1f}s"
                color = COLOR_2_STOP
            else:
                winner_strat = s1
                win_text = "1-STOP STRATEGY"
                diff = (t2 - t1) * 60
                detail = f"Faster by {diff:.1f}s"
                color = COLOR_1_STOP

            self.verdict_label.configure(text=f"{win_text}\n{detail}", text_color=color)
            self.animate_race(team, track, rain, s1, s2)

        except Exception as e:
            self.log_msg(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()

        self.run_btn.configure(state="normal", text="INITIATE STRATEGY", fg_color=COLOR_ACCENT)

    def animate_race(self, team, track, rain, strat1, strat2):
        car1 = self.run_single_race(team, track, rain, strat1)
        car2 = self.run_single_race(team, track, rain, strat2)

        times1 = [x['Time'] for x in car1.history]
        times2 = [x['Time'] for x in car2.history]

        if self.current_canvas: self.current_canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        # --- IMPROVED VISUALS ---
        line1, = ax.plot([], [], color=COLOR_1_STOP, label='1-Stop (Hard/Med)', linewidth=2.5)
        line2, = ax.plot([], [], color=COLOR_2_STOP, label='2-Stop (Aggressive)', linewidth=2.5)

        ax.set_xlim(0, 58)
        min_y = min(min(times1), min(times2)) - 5
        max_y = max(max(times1), max(times2)) + 5
        ax.set_ylim(min_y, max_y)

        ax.set_title(f"LIVE TELEMETRY: {team} @ {track}", color='white', fontsize=12, fontweight='bold')
        ax.set_ylabel("Lap Time (s)", color='white')
        ax.set_xlabel("Lap Number", color='white')
        ax.tick_params(colors='white', which='both')
        ax.grid(True, color='#444444', linestyle='--', alpha=0.5)

        # Better Legend
        legend = ax.legend(frameon=True, facecolor='#2b2b2b', edgecolor='white', labelcolor='white')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.current_canvas = canvas

        def update_frame(frame_idx):
            if frame_idx >= len(times1): return

            line1.set_data(range(1, frame_idx + 2), times1[:frame_idx + 1])
            line2.set_data(range(1, frame_idx + 2), times2[:frame_idx + 1])

            # --- EVENTS LOGGING ---
            # Use car2 (the 2-stopper) to detect general race events
            lap_data = car2.history[frame_idx]

            if lap_data.get('Rain', False):
                self.log_msg(f"L{frame_idx + 1}: RAIN CONDITION ACTIVE")

            if lap_data.get('SC', False):
                self.log_msg(f"L{frame_idx + 1}: SAFETY CAR DEPLOYED")
                ax.axvline(x=frame_idx + 1, color=COLOR_SC, alpha=0.6, linestyle='--')

            # Check 2-Stop Pits
            if lap_data.get('PitStop', False):
                reason = lap_data.get('PitReason', 'Scheduled')
                self.log_msg(f"L{frame_idx + 1} [2-STOP]: BOX! ({reason})")

            # Check 1-Stop Pits
            lap_data_1 = car1.history[frame_idx]
            if lap_data_1.get('PitStop', False):
                reason = lap_data_1.get('PitReason', 'Scheduled')
                self.log_msg(f"L{frame_idx + 1} [1-STOP]: BOX! ({reason})")

            canvas.draw()
            self.after(100, update_frame, frame_idx + 1)

        self.after(100, update_frame, 0)

    def run_single_race(self, team, track, rain, strategy):
        car = RaceCar(team, track, rain)
        car.current_tire = strategy[1][0]
        stops = strategy[0] if isinstance(strategy[0], list) else [strategy[0]]
        tires = strategy[1]
        t_idx = 0

        for lap in range(1, 58):
            reason = "Scheduled"

            # --- SMART PIT REASONING ---
            # Check if previous lap had Safety Car (History has -1, so we check that)
            if car.history and car.history[-1].get('SC', False):
                reason = "SC ADVANTAGE"
            elif car.tire_age > 25 and car.current_tire == 'SOFT':
                reason = "CRITICAL WEAR"
            elif car.is_raining and car.current_tire != 'INTER':
                reason = "WET TRACK"

            if lap in stops:
                t_idx += 1
                if t_idx < len(tires):
                    car.pit_stop(tires[t_idx], reason=reason)
            car.simulate_lap()
        return car


if __name__ == "__main__":
    app = F1SimApp()
    app.mainloop()