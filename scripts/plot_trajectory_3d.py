from simulation_model import AirTrafficModel
import plotly.graph_objects as go
import numpy as np

# =========================
# RUN SIMULATION
# =========================
model = AirTrafficModel()

while any(agent.step_index < len(agent.trajectory) for agent in model.schedule.agents):
    model.step()

fig = go.Figure()

# =========================
# PLOT AIRCRAFT TRAJECTORIES
# =========================
for agent in model.schedule.agents:

    lats = [p[0] for p in agent.history]
    lons = [p[1] for p in agent.history]
    alts = agent.trajectory["Altitude"][:len(lats)]

    fig.add_trace(go.Scatter3d(
        x=lons,
        y=lats,
        z=alts,
        mode='lines',
        name=agent.callsign
    ))

    # =========================
    # PLOT VIOLATION POINTS
    # =========================
    if agent.violation_points:
        vx = [p[0] for p in agent.violation_points]
        vy = [p[1] for p in agent.violation_points]
        vz = [p[2] for p in agent.violation_points]

        fig.add_trace(go.Scatter3d(
            x=vx,
            y=vy,
            z=vz,
            mode='markers',
            marker=dict(size=5, color='red'),
            name=f"{agent.callsign} violations"
        ))

# =========================
# TFR CYLINDER (FIXED - NO BREAKING)
# =========================
tfr_lat = 25.997
tfr_lon = -97.156
radius_km = 30
radius_deg = radius_km / 111

theta = np.linspace(0, 2*np.pi, 50)
z_vals = np.linspace(0, 12000, 20)

x = []
y = []
z = []

# build smooth cylinder points
for zi in z_vals:
    for t in theta:
        x.append(tfr_lon + radius_deg * np.cos(t))
        y.append(tfr_lat + radius_deg * np.sin(t))
        z.append(zi)

fig.add_trace(go.Mesh3d(
    x=x,
    y=y,
    z=z,
    opacity=0.3,
    color='red'
))

# =========================
# CLEAN CAMERA
# =========================
fig.update_layout(
    title="3D Aircraft Trajectories with TFR Cylinder",
    scene=dict(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        zaxis_title="Altitude",
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.2)
        )
    )
)

fig.show()