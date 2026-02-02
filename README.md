F1 Strategy Optimizer: Telemetry-Driven Race Simulation
A high-performance Python framework designed to solve the multi-variable optimization problem of Formula 1 race strategy. This project leverages real-time telemetry and stochastic modeling to predict optimal pit windows and tire compound sequences.


🏎️ The Challenge
In modern motorsport, strategy is an optimization problem where the objective is to minimize total race time under finite resources. This engine accounts for:
Non-linear Tire Degradation: Modeling grip loss based on compound type and age.

Stochastic Variables: Factoring in Safety Car probabilities and traffic density using Monte Carlo simulations.

Game Theory: Calculating "undercut" and "overcut" potential against competitors in a multi-agent environment.


🛠️ Tech Stack
Data: FastF1 for pulling historical lap times and car telemetry.

Processing: NumPy & Pandas for vectorized lap-time evolution calculations.
Sim Engine: Built on Discrete Event Simulation (DES) principles to handle race loops efficiently.

UI: PyQt6 for a professional desktop dashboard to visualize pace and strategy windows.


🔬 Core Components
Physics Engine: Implements differential equations to model the relationship between fuel depletion (car mass) and friction coefficients.
Strategy Solver: A robust optimization framework that identifies the "point of no return" where tire wear overrides the benefit of a lighter fuel load.

Monte Carlo Simulator: Runs thousands of race permutations to output the most reliable pit stop lap Lstop
​
