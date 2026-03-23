import time
import pandas as pd
from simulation_model import AirTrafficModel

# =========================
# INITIALIZE MODEL
# =========================
model = AirTrafficModel()
steps = 500

print("\nStarting simulation...\n")

# =========================
# RUN SIMULATION
# =========================
start_time = time.time()

for step in range(steps):
    model.step()

end_time = time.time()

# =========================
# SUMMARY METRICS
# =========================
total_aircraft = len(model.schedule.agents)
total_separation = sum(model.separation_violations.values())
total_tfr = sum(agent.violation_count for agent in model.schedule.agents)
runtime = round(end_time - start_time, 2)

print("\n===== FINAL SUMMARY =====")
print(f"Total Aircraft: {total_aircraft}")
print(f"Total Separation Events: {total_separation}")
print(f"Total TFR Violations: {total_tfr}")
print(f"Runtime: {runtime} seconds")

# =========================
# TABLE FORMAT OUTPUT
# =========================
data = []

for agent in model.schedule.agents:
    data.append({
        "Callsign": agent.callsign,
        "Separation Violations": model.separation_violations.get(agent.callsign, 0),
        "TFR Violations": agent.violation_count
    })

df = pd.DataFrame(data)

# sort for cleaner view
df = df.sort_values(by="Separation Violations", ascending=False)

print("\n===== PER AIRCRAFT TABLE =====")
print(df.to_string(index=False))