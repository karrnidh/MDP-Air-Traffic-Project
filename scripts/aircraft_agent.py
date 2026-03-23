from mesa import Agent

class AircraftAgent(Agent):

    def __init__(self, model, callsign, trajectory):
        super().__init__(model)

        self.callsign = callsign
        self.trajectory = trajectory.reset_index(drop=True)
        self.step_index = 0

        self.latitude = None
        self.longitude = None
        self.altitude = None

        self.history = []

        # metrics
        self.violation_count = 0
        self.violation_points = []   # ✅ NEW

    def step(self):

        if self.step_index >= len(self.trajectory):
            return

        row = self.trajectory.iloc[self.step_index]

        self.latitude = row["latitude"]
        self.longitude = row["longitude"]
        self.altitude = row["Altitude"]

        self.history.append((self.latitude, self.longitude))

        print(f"{self.callsign} position: {self.latitude:.4f}, {self.longitude:.4f}")

        # TFR violation check
        if self.model.tfr.contains(self.latitude, self.longitude):
            print(f"⚠ WARNING: {self.callsign} entered TFR!")
            self.violation_count += 1

            # store violation point for visualization
            self.violation_points.append((
                self.longitude,
                self.latitude,
                self.altitude
            ))

        self.step_index += 1