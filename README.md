# F1 Strategy Optimizer: Telemetry-Driven Race Simulation

A high-performance Python framework designed to solve the multi-variable optimization problem of Formula 1 race strategy. [cite_start]This project leverages real-time telemetry and stochastic modeling to predict optimal pit windows and tire compound sequences[cite: 5, 25].

## 🏎️ The Challenge
[cite_start]In modern motorsport, race strategy is often the deciding factor between victory and defeat[cite: 18]. [cite_start]This engine treats a Grand Prix as an optimization problem where the objective is to minimize total race time[cite: 19]. 

The system accounts for:
* [cite_start]**Non-linear Tire Degradation:** Modeling grip loss and lap time evolution based on compound type and age[cite: 20, 23, 34].
* [cite_start]**Stochastic Variables:** Factoring in Safety Car probabilities, traffic density, and track incidents using Monte Carlo simulations[cite: 20, 24, 60].
* [cite_start]**Game Theory:** Calculating "undercut" and "overcut" potential against competitors in a multi-agent environment to find subgame perfect equilibrium[cite: 20, 40, 43].

## 🛠️ Tech Stack
* [cite_start]**Data:** `FastF1` for pulling high-fidelity historical lap times and car telemetry[cite: 71, 74].
* [cite_start]**Processing:** `NumPy` & `Pandas` for vectorized lap-time evolution and data manipulation[cite: 74].
* [cite_start]**Sim Engine:** Built on **Discrete Event Simulation (DES)** principles to treat each lap or pit stop as a distinct, interactive event[cite: 46, 48].
* [cite_start]**UI:** `PyQt6` for a professional desktop dashboard to visualize pace and strategic windows[cite: 71, 74].

## 🔬 Core Components
* [cite_start]**Physics Engine:** Implements differential equations to model the relationship between fuel depletion (car mass) and friction coefficients[cite: 53, 54].
* [cite_start]**Strategy Solver:** A robust optimization framework that identifies the "point of no return" where tire wear overrides the benefit of a lighter fuel load[cite: 55, 61].
* [cite_start]**Monte Carlo Simulator:** Runs thousands of race permutations to output the most reliable pit stop lap $L_{stop}$[cite: 71].

## 📈 Project Roadmap (WIP)
* [cite_start]**Phase 1: Research & Data:** Processing datasets and defining mathematical equations for tire wear[cite: 71].
* [cite_start]**Phase 2: Simulation Core:** Implementing the Game Loop and Physics Engine in PyCharm[cite: 71, 75].
* [cite_start]**Phase 3: Optimization:** Developing the Multi-agent logic and Monte Carlo algorithms[cite: 71].
* [cite_start]**Phase 4: Software Deployment:** GUI development and validation against 2023–2025 race results[cite: 71].
