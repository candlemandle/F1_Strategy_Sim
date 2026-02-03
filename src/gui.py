import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
from PIL import Image
import os
import json
import threading
import random
from src.simulation import RaceCar
from src.strategy import StrategyOptimizer

# --- VISUAL CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#1e1e1e"
COLOR_ACCENT = "#E10600"  # F1 Red
COLOR_TEXT_DIM = "#aaaaaa"

# Graph Colors
COLOR_HERO = "#00FFFF"  # Cyan
COLOR_RIVAL = "#FF3399"  # Neon Pink
COLOR_SC = "#FFFF00"  # Yellow


# --- MINI GAME CLASS ---
class MiniGameFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # --- LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # 1. LEADERBOARD (Static Labels)
        self.leaderboard_frame = ctk.CTkFrame(self, fg_color="#151515", corner_radius=0)
        self.leaderboard_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.leaderboard_frame, text="LEGENDS", font=("DIN Alternate", 20, "bold"),
                     text_color="#555").pack(pady=(20, 10))

        self.lb_labels = []
        for i in range(8):
            lbl_name = ctk.CTkLabel(self.leaderboard_frame, text=f"{i + 1}. --", font=("Arial", 12), anchor="w")
            lbl_name.pack(fill="x", padx=20, pady=2)
            lbl_score = ctk.CTkLabel(self.leaderboard_frame, text="0", font=("Arial", 10), text_color="grey")
            lbl_score.place(in_=lbl_name, relx=1.0, rely=0.5, anchor="e")
            self.lb_labels.append((lbl_name, lbl_score))

        # 2. GAME AREA
        self.game_area = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=0)
        self.game_area.grid(row=0, column=1, sticky="nsew")
        self.canvas = ctk.CTkCanvas(self.game_area, bg="#333", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # OVERLAYS
        self.score_label = ctk.CTkLabel(self.game_area, text="SCORE: 0", font=("DIN Alternate", 24, "bold"),
                                        text_color="white", bg_color="#333")
        self.score_label.place(relx=0.5, rely=0.05, anchor="center")
        self.speed_label = ctk.CTkLabel(self.game_area, text="100 km/h", font=("DIN Alternate", 20, "bold"),
                                        text_color="cyan", bg_color="#333")
        self.speed_label.place(relx=0.9, rely=0.05, anchor="e")
        self.start_btn = ctk.CTkButton(self.game_area, text="LIGHTS OUT", command=self.start_game, fg_color="#E10600",
                                       hover_color="#b30500", font=("Arial", 16, "bold"))
        self.start_btn.place(relx=0.5, rely=0.5, anchor="center")

        # STATE
        self.game_running = False
        self.paused = False
        self.car_x = 0;
        self.car_y = 0
        self.obstacles = []
        self.score = 0;
        self.kmh = 100
        self.lane_offset = 0
        self.unique_id_counter = 0

        self.legends = [("Max Verstappen", 10000), ("Lewis Hamilton", 8500), ("Fernando Alonso", 7000),
                        ("Charles Leclerc", 5500), ("Lando Norris", 4000), ("Oscar Piastri", 2500),
                        ("Logan Sargeant", 1000)]

        self.canvas.bind("<Left>", self.move_left)
        self.canvas.bind("<Right>", self.move_right)
        self.canvas.bind("<p>", self.toggle_pause)

        self.update_leaderboard_data()

    def update_leaderboard_data(self):
        standings = self.legends + [("YOU", self.score)]
        standings.sort(key=lambda x: x[1], reverse=True)

        for i, (name, pts) in enumerate(standings[:8]):
            lbl_n, lbl_s = self.lb_labels[i]
            color = "#E10600" if name == "YOU" else "white"
            font = ("Arial", 14, "bold") if name == "YOU" else ("Arial", 12)
            lbl_n.configure(text=f"{i + 1}. {name}", text_color=color, font=font)
            lbl_s.configure(text=f"{pts}")

    def draw_f1_car(self, x, y, color="red", unique_tag=None):
        if unique_tag is None: unique_tag = "player" if color == "red" else "enemy"
        c_body = "#E10600" if color == "red" else "#00FFFF"
        c_wing = "white" if color == "red" else "#888"

        self.canvas.create_rectangle(x - 18, y - 20, x - 10, y - 6, fill="#111", tags=unique_tag)
        self.canvas.create_rectangle(x + 10, y - 20, x + 18, y - 6, fill="#111", tags=unique_tag)
        self.canvas.create_rectangle(x - 18, y + 15, x - 10, y + 29, fill="#111", tags=unique_tag)
        self.canvas.create_rectangle(x + 10, y + 15, x + 18, y + 29, fill="#111", tags=unique_tag)
        self.canvas.create_rectangle(x - 6, y - 25, x + 6, y + 25, fill=c_body, outline="", tags=unique_tag)
        self.canvas.create_rectangle(x - 16, y - 30, x + 16, y - 25, fill=c_wing, outline="", tags=unique_tag)
        self.canvas.create_rectangle(x - 14, y + 25, x + 14, y + 30, fill="#111", outline="", tags=unique_tag)
        self.canvas.create_rectangle(x - 2, y - 5, x + 2, y + 2, fill="yellow", tags=unique_tag)

    def start_game(self):
        self.start_btn.place_forget()
        self.canvas.delete("all")
        self.game_running = True
        self.paused = False
        self.score = 0;
        self.kmh = 100
        self.obstacles = []
        self.lane_offset = 0
        self.canvas.focus_set()

        w = self.canvas.winfo_width();
        h = self.canvas.winfo_height()
        if w < 100: w = 800; h = 600

        # Reset Player
        self.car_x = int(w / 2)
        self.car_y = int(h - 120)
        self.draw_f1_car(self.car_x, self.car_y, "red", "player")
        self.update_leaderboard_data()

        # Start Loop
        self.game_loop()

    def toggle_pause(self, event=None):
        if not self.game_running: return
        self.paused = not self.paused
        if self.paused:
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, text="PAUSED",
                                    fill="white", font=("Arial", 30), tags="pause_text")
        else:
            self.canvas.delete("pause_text"); self.game_loop()

    def game_loop(self):
        if not self.game_running or self.paused: return

        w = self.canvas.winfo_width();
        h = self.canvas.winfo_height()
        if w < 100: w = 800

        # --- 1. SPEED ---
        # +25 km/h every 250 points
        target_kmh = 100 + int(self.score / 250) * 25
        self.kmh = target_kmh
        px_speed = int(self.kmh / 12)
        self.speed_label.configure(text=f"{self.kmh} km/h")

        # --- 2. DRAW ROAD (Bulletproof: Redraw every frame) ---
        self.canvas.delete("road_line")
        self.lane_offset = (self.lane_offset + px_speed) % 80

        for col in range(1, 4):
            x = int(w * (col / 4))
            # Draw dashed line from top to bottom
            for y in range(-100, h + 100, 80):
                final_y = y + self.lane_offset
                self.canvas.create_line(x, final_y, x, final_y + 40, fill="#555", width=3, tags="road_line")

        # Ensure Player is on top of road
        self.canvas.tag_raise("player")

        # --- 3. SPAWN ENEMIES (Free Roam) ---
        spawn_rate = 5 + int(self.score / 500)
        if random.randint(0, 100) < spawn_rate:
            # Random X position (not locked to lanes)
            test_x = random.randint(50, w - 50)

            # Anti-Overlap Check
            clear = True
            for obs in self.obstacles:
                if obs['y'] < 250 and abs(obs['x'] - test_x) < 70:
                    clear = False;
                    break

            if clear:
                self.unique_id_counter += 1
                tag_id = f"enemy_{self.unique_id_counter}"
                self.draw_f1_car(test_x, -100, "silver", tag_id)
                # Enemies move slightly faster than road (visual overtaking)
                obs_speed = px_speed + random.randint(2, 6)
                self.obstacles.append({'tag': tag_id, 'speed': obs_speed, 'x': test_x, 'y': -100})

        # --- 4. MOVE & COLLIDE ---
        for obs in self.obstacles[:]:
            self.canvas.move(obs['tag'], 0, obs['speed'])
            obs['y'] += obs['speed']
            self.canvas.tag_raise(obs['tag'])  # Ensure enemies are on top of road

            # Hitbox Logic (35px width, 55px height)
            if abs(self.car_x - obs['x']) < 35 and abs(self.car_y - obs['y']) < 55:
                self.game_over()
                return

            # Score Update
            if obs['y'] > h + 50:
                self.canvas.delete(obs['tag'])
                self.obstacles.remove(obs)
                self.score += 10
                self.score_label.configure(text=f"SCORE: {self.score}")

                # Update leaderboard sparingly (performance)
                if self.score % 200 == 0: self.update_leaderboard_data()

        self.after(30, self.game_loop)

    def move_left(self, event):
        if self.game_running and not self.paused and self.car_x > 40:
            self.car_x -= 20
            self.canvas.move("player", -20, 0)

    def move_right(self, event):
        w = self.canvas.winfo_width()
        if self.game_running and not self.paused and self.car_x < w - 40:
            self.car_x += 20
            self.canvas.move("player", 20, 0)

    def game_over(self):
        self.game_running = False
        self.update_leaderboard_data()
        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, text="CRASHED!",
                                fill="#E10600", font=("DIN Alternate", 40, "bold"))
        self.start_btn.configure(text="RESTART SEASON")
        self.start_btn.place(relx=0.5, rely=0.6, anchor="center")

class F1SimApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("F1 STRATEGY SIMULATOR 2026 - ULTIMATE")
        self.geometry("1400x950")
        self.configure(fg_color=COLOR_BG)

        self.teams_list = sorted(self.load_json_keys('team_db.json', ["Red Bull Racing", "Ferrari"]))
        self.tracks_list = sorted(self.load_json_keys('track_db.json', ["Bahrain", "Monza"]))

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#151515")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="RACE CONTROL", font=("DIN Alternate", 24, "bold"), text_color="white").pack(
            pady=(30, 10))

        self.mode_var = ctk.StringVar(value="STRATEGY")
        self.mode_switch = ctk.CTkSegmentedButton(self.sidebar,
                                                  values=["STRATEGY", "VERSUS", "HUMAN vs AI", "MONTE CARLO", "ARCADE"],
                                                  command=self.change_mode,
                                                  variable=self.mode_var,
                                                  fg_color="#333", selected_color=COLOR_ACCENT)
        self.mode_switch.pack(fill="x", padx=20, pady=(0, 20))

        # STANDARD CONTROLS FRAME
        self.controls_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.controls_frame.pack(fill="both", expand=True)

        self.create_label(self.controls_frame, "CONSTRUCTOR")
        self.team_menu = ctk.CTkOptionMenu(self.controls_frame, values=self.teams_list, fg_color="#333",
                                           button_color="#008888")
        self.team_menu.pack(fill="x", padx=20, pady=5)

        self.rival_label = ctk.CTkLabel(self.controls_frame, text="RIVAL CONSTRUCTOR", font=("Arial", 11, "bold"),
                                        text_color=COLOR_TEXT_DIM)
        self.rival_menu = ctk.CTkOptionMenu(self.controls_frame, values=self.teams_list, fg_color="#333",
                                            button_color="#880044")
        self.rival_menu.set(self.teams_list[1] if len(self.teams_list) > 1 else self.teams_list[0])

        self.create_label(self.controls_frame, "CIRCUIT")
        self.track_menu = ctk.CTkOptionMenu(self.controls_frame, values=self.tracks_list, fg_color="#333",
                                            button_color="#444", command=self.load_track_map)
        self.track_menu.pack(fill="x", padx=20, pady=5)

        self.create_label(self.controls_frame, "METEOROLOGY")
        self.rain_val_label = ctk.CTkLabel(self.controls_frame, text="0% CHANCE", text_color=COLOR_ACCENT,
                                           font=("Arial", 12, "bold"))
        self.rain_val_label.pack(anchor="e", padx=20)
        self.rain_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=100, number_of_steps=100,
                                         progress_color=COLOR_ACCENT, command=self.update_rain_text)
        self.rain_slider.set(0);
        self.rain_slider.pack(fill="x", padx=20, pady=5)

        self.sc_label = ctk.CTkLabel(self.controls_frame, text="SC RISK: 2%", text_color="orange",
                                     font=("Arial", 12, "bold"))
        self.sc_label.pack(anchor="e", padx=20, pady=(10, 0))
        self.sc_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=20, number_of_steps=20, progress_color="orange",
                                       command=lambda v: self.sc_label.configure(text=f"SC RISK: {int(v)}%"))
        self.sc_slider.set(2);
        self.sc_slider.pack(fill="x", padx=20, pady=5)

        # STRATEGY BUILDER
        self.user_strat_frame = ctk.CTkFrame(self.controls_frame, fg_color="#222")
        ctk.CTkLabel(self.user_strat_frame, text="YOUR STRATEGY", text_color="cyan", font=("Arial", 12, "bold")).pack(
            pady=5)
        self.user_tire1 = ctk.CTkOptionMenu(self.user_strat_frame, values=["SOFT", "MEDIUM", "HARD"], width=100,
                                            fg_color="#444")
        self.user_tire1.pack(pady=2);
        self.user_tire1.set("SOFT")
        self.lbl_pit1 = ctk.CTkLabel(self.user_strat_frame, text="PIT LAP: 20")
        self.lbl_pit1.pack()
        self.slider_pit1 = ctk.CTkSlider(self.user_strat_frame, from_=1, to=56, number_of_steps=56,
                                         command=lambda v: self.lbl_pit1.configure(text=f"PIT LAP: {int(v)}"))
        self.slider_pit1.set(20);
        self.slider_pit1.pack(fill="x", padx=10)
        self.user_tire2 = ctk.CTkOptionMenu(self.user_strat_frame, values=["SOFT", "MEDIUM", "HARD"], width=100,
                                            fg_color="#444")
        self.user_tire2.pack(pady=5);
        self.user_tire2.set("HARD")
        self.use_2stop = ctk.CTkCheckBox(self.user_strat_frame, text="Add 2nd Stop", font=("Arial", 11),
                                         command=self.toggle_2nd_stop)
        self.use_2stop.pack(pady=5)
        self.pit2_group = ctk.CTkFrame(self.user_strat_frame, fg_color="transparent")
        self.lbl_pit2 = ctk.CTkLabel(self.pit2_group, text="PIT 2 LAP: 40");
        self.lbl_pit2.pack()
        self.slider_pit2 = ctk.CTkSlider(self.pit2_group, from_=1, to=56, number_of_steps=56,
                                         command=lambda v: self.lbl_pit2.configure(text=f"PIT 2 LAP: {int(v)}"))
        self.slider_pit2.set(40);
        self.slider_pit2.pack(fill="x", padx=10)
        self.user_tire3 = ctk.CTkOptionMenu(self.pit2_group, values=["SOFT", "MEDIUM", "HARD"], width=100,
                                            fg_color="#444")
        self.user_tire3.pack(pady=5);
        self.user_tire3.set("SOFT")

        self.run_btn = ctk.CTkButton(self.controls_frame, text="INITIATE SIMULATION", height=50,
                                     fg_color=COLOR_ACCENT, hover_color="#b30500", font=("DIN Alternate", 16, "bold"),
                                     command=self.start_simulation_thread)
        self.run_btn.pack(side="bottom", fill="x", padx=20, pady=40)

        # ================= CENTER PANEL =================
        self.center_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Standard Graph Frame
        self.graph_frame = ctk.CTkFrame(self.center_panel, fg_color="#2b2b2b", corner_radius=10)
        self.graph_frame.pack(fill="both", expand=True)

        # Arcade Frame
        self.game_frame = MiniGameFrame(self.center_panel, fg_color="#111", corner_radius=10)

        self.current_canvas = None
        self.verdict_frame = ctk.CTkFrame(self.center_panel, height=100, fg_color="#2b2b2b", corner_radius=10)
        self.verdict_frame.pack(fill="x", pady=(20, 0))
        self.verdict_label = ctk.CTkLabel(self.verdict_frame, text="AWAITING DATA...", font=("Arial", 20, "bold"))
        self.verdict_label.place(relx=0.5, rely=0.5, anchor="center")

        # ================= RIGHT PANEL =================
        self.right_panel = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#1a1a1a")
        self.right_panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="TRACK INTEL", font=("DIN Alternate", 18, "bold")).pack(pady=(20, 5))
        self.map_label = ctk.CTkLabel(self.right_panel, text="[NO MAP]", width=250, height=130, fg_color="#111",
                                      corner_radius=8)
        self.map_label.pack(pady=5)

        self.telemetry_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.telemetry_container.pack(fill="x", padx=10, pady=10)

        # HERO TELEMETRY
        self.tel_hero_frame = ctk.CTkFrame(self.telemetry_container, fg_color="#222")
        self.tel_hero_frame.pack(fill="x", pady=5)
        self.lbl_hero_name = ctk.CTkLabel(self.tel_hero_frame, text="HERO CAR", font=("Arial", 10, "bold"),
                                          text_color=COLOR_HERO)
        self.lbl_hero_name.pack(anchor="w", padx=10, pady=(5, 0))
        self.lbl_hero_health = ctk.CTkLabel(self.tel_hero_frame, text="TIRES: 100%", font=("Arial", 10));
        self.lbl_hero_health.pack(anchor="w", padx=10)
        self.bar_hero_tire = ctk.CTkProgressBar(self.tel_hero_frame, height=8, progress_color="green")
        self.bar_hero_tire.set(1.0);
        self.bar_hero_tire.pack(fill="x", padx=10, pady=5)
        self.lbl_hero_stats = ctk.CTkLabel(self.tel_hero_frame, text="PACE: -- | FUEL: 110kg", font=("Consolas", 10));
        self.lbl_hero_stats.pack(anchor="e", padx=10, pady=(0, 5))

        # RIVAL TELEMETRY
        self.tel_rival_frame = ctk.CTkFrame(self.telemetry_container, fg_color="#222")
        self.tel_rival_frame.pack(fill="x", pady=5)
        self.lbl_rival_name = ctk.CTkLabel(self.tel_rival_frame, text="RIVAL CAR", font=("Arial", 10, "bold"),
                                           text_color=COLOR_RIVAL)
        self.lbl_rival_name.pack(anchor="w", padx=10, pady=(5, 0))
        self.lbl_rival_health = ctk.CTkLabel(self.tel_rival_frame, text="TIRES: 100%", font=("Arial", 10));
        self.lbl_rival_health.pack(anchor="w", padx=10)
        self.bar_rival_tire = ctk.CTkProgressBar(self.tel_rival_frame, height=8, progress_color="green")
        self.bar_rival_tire.set(1.0);
        self.bar_rival_tire.pack(fill="x", padx=10, pady=5)
        self.lbl_rival_stats = ctk.CTkLabel(self.tel_rival_frame, text="PACE: -- | FUEL: 110kg", font=("Consolas", 10));
        self.lbl_rival_stats.pack(anchor="e", padx=10, pady=(0, 5))

        # LOG
        ctk.CTkLabel(self.right_panel, text="TIMING LOG", font=("DIN Alternate", 14, "bold"), anchor="w").pack(fill="x",
                                                                                                               padx=15,
                                                                                                               pady=(10,
                                                                                                                     5))
        self.log_box = ctk.CTkTextbox(self.right_panel, height=250, fg_color="#111", text_color="#00ff00",
                                      font=("Consolas", 12))
        self.log_box.pack(fill="x", padx=15, pady=5)
        self.log_box.tag_config("white", foreground="white")
        self.log_box.tag_config("yellow", foreground="#FFD700")
        self.log_box.tag_config("red", foreground="#FF4444")
        self.log_box.tag_config("blue", foreground="#44DDFF")

        self.load_track_map(self.track_menu.get())
        self.change_mode("STRATEGY")

    # --- UI LOGIC ---
    def change_mode(self, mode):
        # Reset Widgets
        self.rival_label.pack_forget();
        self.rival_menu.pack_forget();
        self.user_strat_frame.pack_forget()

        # ARCADE LOGIC
        if mode == "ARCADE":
            self.controls_frame.pack_forget()
            self.graph_frame.pack_forget()
            self.verdict_frame.pack_forget()
            self.right_panel.grid_remove()  # Hide Right Panel
            self.game_frame.pack(fill="both", expand=True)
            self.game_frame.focus_set()  # CRITICAL FIX
            return
        else:
            self.game_frame.pack_forget()
            self.controls_frame.pack(fill="both", expand=True)
            self.graph_frame.pack(fill="both", expand=True)
            self.verdict_frame.pack(fill="x", pady=(20, 0))
            self.right_panel.grid(row=0, column=2, sticky="nsew")

        # Standard Modes Logic
        self.telemetry_container.pack(fill="x", padx=10, pady=10, before=self.log_box)
        if mode == "VERSUS":
            self.rival_label.pack(anchor="w", padx=20, pady=(10, 0), after=self.team_menu)
            self.rival_menu.pack(fill="x", padx=20, pady=5, after=self.rival_label)
        elif mode == "HUMAN vs AI":
            self.user_strat_frame.pack(fill="x", padx=10, pady=10, after=self.rain_slider)
        elif mode == "MONTE CARLO":
            self.telemetry_container.pack_forget()

    def toggle_2nd_stop(self):
        if self.use_2stop.get() == 1:
            self.pit2_group.pack(fill="x", pady=5)
        else:
            self.pit2_group.pack_forget()

    def update_rain_text(self, value):
        self.rain_val_label.configure(text=f"{int(value)}% CHANCE")

    def create_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 11, "bold"), text_color=COLOR_TEXT_DIM).pack(anchor="w", padx=20,
                                                                                                    pady=(20, 5))

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
                    found = True;
                    break
                except:
                    pass
        if not found: self.map_label.configure(image=None, text=f"NO MAP FOR\n{track_name.upper()}")

    def log_msg(self, msg, color="white"):
        self.log_box.insert("end", f">> {msg}\n", color)
        self.log_box.see("end")

    # --- SIMULATION ---
    def start_simulation_thread(self):
        self.run_btn.configure(state="disabled", text="CALCULATING...", fg_color="#555")
        self.log_box.delete("0.0", "end")
        threading.Thread(target=self.run_process).start()

    def run_process(self):
        mode = self.mode_var.get()
        team = self.team_menu.get()
        track = self.track_menu.get()
        rain = int(self.rain_slider.get())
        self.log_msg(f"MODE: {mode}")
        try:
            if mode == "STRATEGY":
                self.run_strategy_mode(team, track, rain)
            elif mode == "VERSUS":
                self.run_versus_mode(team, self.rival_menu.get(), track, rain)
            elif mode == "HUMAN vs AI":
                self.run_human_vs_ai(team, track, rain)
            elif mode == "MONTE CARLO":
                self.run_monte_carlo_mode(team, track, rain)
        except Exception as e:
            self.log_msg(f"ERROR: {e}", "red")
            import traceback
            traceback.print_exc()
        self.run_btn.configure(state="normal", text="INITIATE SIMULATION", fg_color=COLOR_ACCENT)

    def run_strategy_mode(self, team, track, rain):
        optimizer = StrategyOptimizer(team=team, track=track, rain_prob=rain)
        t1, s1 = optimizer.find_optimal_1_stop()
        t2, s2 = optimizer.find_optimal_2_stop()
        if t2 < t1:
            win, col, det = "2-STOP WINS", COLOR_RIVAL, f"Gap: -{(t1 - t2) * 60:.1f}s"
        else:
            win, col, det = "1-STOP WINS", COLOR_HERO, f"Gap: -{(t2 - t1) * 60:.1f}s"
        self.verdict_label.configure(text=f"{win}\n{det}", text_color=col)
        self.lbl_hero_name.configure(text="1-STOP STRATEGY", text_color=COLOR_HERO)
        self.lbl_rival_name.configure(text="2-STOP STRATEGY", text_color=COLOR_RIVAL)
        self.animate_graph(self.run_single_race(team, track, rain, s1), self.run_single_race(team, track, rain, s2),
                           "1-Stop", "2-Stop", f"{team} Strategy")

    def run_versus_mode(self, hero, rival, track, rain):
        opt_h = StrategyOptimizer(team=hero, track=track, rain_prob=rain)
        t1, s1 = opt_h.find_optimal_1_stop();
        t2, s2 = opt_h.find_optimal_2_stop()
        h_strat = s2 if t2 < t1 else s1
        opt_r = StrategyOptimizer(team=rival, track=track, rain_prob=rain)
        rt1, rs1 = opt_r.find_optimal_1_stop();
        rt2, rs2 = opt_r.find_optimal_2_stop()
        r_strat = rs2 if rt2 < rt1 else rs1
        c_hero = self.run_single_race(hero, track, rain, h_strat)
        c_rival = self.run_single_race(rival, track, rain, r_strat)
        diff = abs(c_hero.total_race_time - c_rival.total_race_time)
        if c_hero.total_race_time < c_rival.total_race_time:
            win, col = f"{hero.upper()} WINS", COLOR_HERO
        else:
            win, col = f"{rival.upper()} WINS", COLOR_RIVAL
        self.verdict_label.configure(text=f"{win}\nGap: {diff:.1f}s", text_color=col)
        self.lbl_hero_name.configure(text=hero.upper(), text_color=COLOR_HERO)
        self.lbl_rival_name.configure(text=rival.upper(), text_color=COLOR_RIVAL)
        self.animate_graph(c_hero, c_rival, hero, rival, f"{hero} vs {rival}")

    def run_human_vs_ai(self, team, track, rain):
        opt = StrategyOptimizer(team=team, track=track, rain_prob=rain)
        t1, s1 = opt.find_optimal_1_stop();
        t2, s2 = opt.find_optimal_2_stop()
        ai_strat = s2 if t2 < t1 else s1
        stops = [int(self.slider_pit1.get())]
        tires = [self.user_tire1.get(), self.user_tire2.get()]
        if self.use_2stop.get() == 1:
            stops.append(int(self.slider_pit2.get()));
            tires.append(self.user_tire3.get());
            stops.sort()
        c_human = self.run_single_race(team, track, rain, (stops, tires))
        c_ai = self.run_single_race(team, track, rain, ai_strat)
        diff = abs(c_human.total_race_time - c_ai.total_race_time)
        if c_human.total_race_time < c_ai.total_race_time:
            win, col = "USER WINS!", COLOR_HERO
        else:
            win, col = "AI MODEL WINS", COLOR_RIVAL
        self.verdict_label.configure(text=f"{win}\nGap: {diff:.1f}s", text_color=col)
        self.lbl_hero_name.configure(text="USER STRATEGY", text_color=COLOR_HERO)
        self.lbl_rival_name.configure(text="AI STRATEGY", text_color=COLOR_RIVAL)
        self.animate_graph(c_human, c_ai, "User Strategy", "AI Strategy", f"Man vs Machine: {team}")

    def run_monte_carlo_mode(self, team, track, rain):
        self.log_msg("Running 500 Simulations...")
        opt = StrategyOptimizer(team=team, track=track, rain_prob=rain)
        _, s1 = opt.find_optimal_1_stop();
        _, s2 = opt.find_optimal_2_stop()
        w1, w2 = 0, 0
        for _ in range(500):
            if self.run_single_race(team, track, rain, s1).total_race_time < self.run_single_race(team, track, rain,
                                                                                                  s2).total_race_time:
                w1 += 1
            else:
                w2 += 1
        if self.current_canvas: self.current_canvas.get_tk_widget().destroy()
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100);
        fig.patch.set_facecolor('#2b2b2b')
        ax.pie([w1, w2], labels=[f'1-Stop ({w1 / 5:.1f}%)', f'2-Stop ({w2 / 5:.1f}%)'],
               colors=[COLOR_HERO, COLOR_RIVAL], autopct='%1.1f%%', startangle=90, textprops={'color': "white"})
        ax.set_title(f"Monte Carlo Analysis (N=500)", color='white')
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.current_canvas = canvas;
        self.verdict_label.configure(text="PROBABILITY CALCULATED", text_color="white")

    def paint_tire_zones(self, ax, history):
        colors = {'SOFT': ('#ff3333', 0.15), 'MEDIUM': ('#ffff33', 0.15), 'HARD': ('#ffffff', 0.1),
                  'INTER': ('#33ccff', 0.2)}
        patches = [Patch(facecolor=c[0], alpha=0.3, label=n) for n, c in colors.items()]
        ax.add_artist(ax.legend(handles=patches, loc='upper center', ncol=4, frameon=False, labelcolor='white'))
        start = 0;
        cur = history[0]['Compound']
        for i, lap in enumerate(history):
            if lap['Compound'] != cur or i == len(history) - 1:
                c = colors.get(cur, ('#333', 0.1))
                ax.axvspan(start, i, facecolor=c[0], alpha=c[1]);
                cur = lap['Compound'];
                start = i

    def animate_graph(self, c1, c2, l1, l2, title):
        if self.current_canvas: self.current_canvas.get_tk_widget().destroy()
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100);
        fig.patch.set_facecolor('#2b2b2b');
        ax.set_facecolor('#2b2b2b')
        self.paint_tire_zones(ax, c1.history)
        line1, = ax.plot([], [], color=COLOR_HERO, label=l1, linewidth=2.5)
        line2, = ax.plot([], [], color=COLOR_RIVAL, label=l2, linewidth=2.5)
        ax.set_xlim(0, 58);
        times = [x['Time'] for x in c1.history] + [x['Time'] for x in c2.history];
        ax.set_ylim(min(times) - 5, max(times) + 5)
        ax.set_title(title, color='white', fontweight='bold');
        ax.set_ylabel("Lap Time (s)", color='white');
        ax.set_xlabel("Lap Number", color='white')
        ax.tick_params(colors='white');
        ax.grid(True, color='#444', linestyle='--', alpha=0.5)
        ax.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True);
        self.current_canvas = canvas

        def update(frame):
            if frame >= len(c1.history): return
            line1.set_data(range(1, frame + 2), [x['Time'] for x in c1.history[:frame + 1]])
            line2.set_data(range(1, frame + 2), [x['Time'] for x in c2.history[:frame + 1]])

            def update_car_stats(history, bar, lbl_health, lbl_stats):
                lap = history[frame]
                health = lap.get('Health', 100);
                fuel = lap.get('Fuel', 0);
                pace = lap['Time']
                bar.set(health / 100.0)
                color = "green" if health > 50 else "orange" if health > 20 else "red"
                bar.configure(progress_color=color)
                lbl_health.configure(text=f"TIRES: {health}%", text_color=color)
                lbl_stats.configure(text=f"PACE: {pace:.1f}s | FUEL: {fuel:.1f}kg")

            update_car_stats(c1.history, self.bar_hero_tire, self.lbl_hero_health, self.lbl_hero_stats)
            update_car_stats(c2.history, self.bar_rival_tire, self.lbl_rival_health, self.lbl_rival_stats)

            h_lap = c1.history[frame]
            if h_lap.get('SC'): self.log_msg(f"L{frame + 1}: SAFETY CAR", "red"); ax.axvline(x=frame + 1,
                                                                                             color=COLOR_SC, alpha=0.8,
                                                                                             linestyle='--')
            if h_lap.get('PitStop'): self.log_msg(f"L{frame + 1} [{l1}]: BOX!", "yellow"); ax.plot(frame, h_lap['Time'],
                                                                                                   'o', color='white',
                                                                                                   markeredgecolor=COLOR_HERO,
                                                                                                   zorder=5)
            if c2.history[frame].get('PitStop'): self.log_msg(f"L{frame + 1} [{l2}]: BOX!", "yellow"); ax.plot(frame,
                                                                                                               c2.history[
                                                                                                                   frame][
                                                                                                                   'Time'],
                                                                                                               'o',
                                                                                                               color='white',
                                                                                                               markeredgecolor=COLOR_RIVAL,
                                                                                                               zorder=5)

            canvas.draw()
            self.after(100, update, frame + 1)

        self.after(100, update, 0)

    def run_single_race(self, team, track, rain, strategy):
        car = RaceCar(team, track, rain)
        car.current_tire = strategy[1][0]
        stops = strategy[0] if isinstance(strategy[0], list) else [strategy[0]]
        tires = strategy[1];
        t_idx = 0
        for lap in range(1, 58):
            reason = "Scheduled"
            if car.history and car.history[-1].get('SC'):
                reason = "SC ADVANTAGE"
            elif car.is_raining and car.current_tire != 'INTER':
                reason = "WET TRACK"
            if lap in stops:
                t_idx += 1
                if t_idx < len(tires): car.pit_stop(tires[t_idx], reason)
            car.simulate_lap()
        return car


if __name__ == "__main__":
    app = F1SimApp()
    app.mainloop()