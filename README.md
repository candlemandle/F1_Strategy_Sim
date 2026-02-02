# F1 Strategy Optimizer: Telemetry-Driven Race Simulation

A high-performance Python framework designed to solve the multi-variable optimization problem of Formula 1 race strategy. This project leverages real-time telemetry and stochastic modeling to predict optimal pit windows and tire compound sequences.

## 🏎️ The Challenge
In modern motorsport, race strategy is often the deciding factor between victory and defeat. This engine treats a Grand Prix as an optimization problem where the objective is to minimize total race time. 

The system accounts for:
* **Non-linear Tire Degradation:** Modeling grip loss and lap time evolution based on compound type and age.
* **Stochastic Variables:** Factoring in Safety Car probabilities, traffic density, and track incidents using Monte Carlo simulations.
* **Game Theory:** Calculating "undercut" and "overcut" potential against competitors in a multi-agent environment to find subgame perfect equilibrium.

## 🛠️ Tech Stack
* **Data:** `FastF1` for pulling high-fidelity historical lap times and car telemetry.
* **Processing:** `NumPy` & `Pandas` for vectorized lap-time evolution and data manipulation.
* **Sim Engine:** Built on **Discrete Event Simulation (DES)** principles to treat each lap or pit stop as a distinct, interactive event.
* **UI:** `PyQt6` for a professional desktop dashboard to visualize pace and strategic windows.

## 🔬 Core Components
* **Physics Engine:** Implements differential equations to model the relationship between fuel depletion (car mass) and friction coefficients.
* **Strategy Solver:** A robust optimization framework that identifies the "point of no return" where tire wear overrides the benefit of a lighter fuel load.
* **Monte Carlo Simulator:** Runs thousands of race permutations to output the most reliable pit stop lap $L_{stop}$.

## 📈 Project Roadmap (WIP)
* **Phase 1: Research & Data:** Processing datasets and defining mathematical equations for tire wear.
* **Phase 2: Simulation Core:** Implementing the Game Loop and Physics Engine in PyCharm.
* **Phase 3: Optimization:** Developing the Multi-agent logic and Monte Carlo algorithms.
* **Phase 4: Software Deployment:** GUI development and validation against 2023–2025 race results.
