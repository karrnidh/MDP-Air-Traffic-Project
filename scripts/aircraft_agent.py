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

        # =========================
        # METRICS
        # =========================
        self.violation_count = 0
        self.violation_points = []

        # =========================
        # TFR TRACKING
        # =========================
        self.in_tfr = False          # track if currently inside
        self.tfr_cooldown = 0        # prevent rapid re-counting

    def step(self):

        if self.step_index >= len(self.trajectory):
            return

        row = self.trajectory.iloc[self.step_index]

        self.latitude = row["latitude"]
        self.longitude = row["longitude"]
        self.altitude = row["Altitude"]

        self.history.append((self.latitude, self.longitude))

        print(f"{self.callsign} position: {self.latitude:.4f}, {self.longitude:.4f}")

        # =========================
        # TFR VIOLATION CHECK (FINAL FIX)
        # =========================
        inside_tfr = self.model.tfr.contains(self.latitude, self.longitude)

        # reduce cooldown each step
        if self.tfr_cooldown > 0:
            self.tfr_cooldown -= 1

        # count only valid entry (with cooldown protection)
        if inside_tfr and not self.in_tfr and self.tfr_cooldown == 0:
            print(f"⚠ WARNING: {self.callsign} ENTERED TFR!")
            self.violation_count += 1

            self.violation_points.append((
                self.longitude,
                self.latitude,
                self.altitude
            ))

            # prevent jitter-based multiple counts
            self.tfr_cooldown = 20

        # update state
        self.in_tfr = inside_tfr

        self.step_index += 1