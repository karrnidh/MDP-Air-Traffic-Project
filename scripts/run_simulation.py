from simulation_model import AirTrafficModel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# initialize model
model = AirTrafficModel()

print("\nStarting simulation...\n")

step = 0

# run until all aircraft finish
while any(agent.step_index < len(agent.trajectory) for agent in model.schedule.agents):
    
    print(f"\n--- Simulation Step {step} ---")
    model.step()
    step += 1

print("\nSimulation complete!\n")

# =========================
# SAVE RESULTS TO CSV
# =========================
results = []

for agent in model.schedule.agents:
    results.append({
        "Callsign": agent.callsign,
        "Total Steps": len(agent.history),
        "TFR Violations": agent.violation_count
    })

df = pd.DataFrame(results)

df.to_csv("simulation_results.csv", index=False)

print("Results saved to simulation_results.csv")
print(df)

# =========================
# PLOT TRAJECTORIES
# =========================
plt.figure(figsize=(10, 7))

for agent in model.schedule.agents:
    lats = [pos[0] for pos in agent.history]
    lons = [pos[1] for pos in agent.history]

    plt.plot(lons, lats, label=agent.callsign)

# TFR circle
tfr_lat = 25.997
tfr_lon = -97.156
radius_km = 30
radius_deg = radius_km / 111

theta = np.linspace(0, 2 * np.pi, 100)

circle_lat = tfr_lat + radius_deg * np.sin(theta)
circle_lon = tfr_lon + radius_deg * np.cos(theta)

plt.plot(circle_lon, circle_lat, linestyle='--', label='TFR Zone')

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Simulated Aircraft Trajectories")
plt.legend()
plt.grid(True)

plt.show()