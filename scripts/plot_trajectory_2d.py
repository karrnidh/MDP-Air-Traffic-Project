from simulation_model import AirTrafficModel
import matplotlib.pyplot as plt
import numpy as np

model = AirTrafficModel()

# run simulation
while any(agent.step_index < len(agent.trajectory) for agent in model.schedule.agents):
    model.step()

# plot
plt.figure(figsize=(10,7))

# aircraft trajectories
for agent in model.schedule.agents:
    lats = [p[0] for p in agent.history]
    lons = [p[1] for p in agent.history]

    plt.plot(lons, lats, label=agent.callsign)

# TFR overlay
tfr_lat = 25.997
tfr_lon = -97.156
radius_km = 30
radius_deg = radius_km / 111

theta = np.linspace(0, 2*np.pi, 100)

circle_lat = tfr_lat + radius_deg * np.sin(theta)
circle_lon = tfr_lon + radius_deg * np.cos(theta)

plt.plot(circle_lon, circle_lat, 'r--', linewidth=2, label="TFR Zone")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Aircraft Trajectories with TFR (2D)")
plt.legend()
plt.grid(True)

plt.show()