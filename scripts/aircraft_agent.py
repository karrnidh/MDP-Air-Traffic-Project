from mesa import Agent
import math


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

        #
        # METRICS
        #
        self.violation_count = 0
        self.violation_points = []
        self.avoidance_count = 0
        self.total_distance = 0   

        #
        # TFR TRACKING
        #
        self.in_tfr = False
        self.tfr_cooldown = 20

    def step(self):

        if self.step_index >= len(self.trajectory):
            return

        row = self.trajectory.iloc[self.step_index]

        new_lat = row["latitude"]
        new_lon = row["longitude"]
        new_alt = row["Altitude"]

        #
        # DISTANCE CALCULATION (NEW)
        #
        if self.latitude is not None:
            dlat = new_lat - self.latitude
            dlon = new_lon - self.longitude
            step_distance = math.sqrt(dlat**2 + dlon**2) * 111
            self.total_distance += step_distance

        # update position
        self.latitude = new_lat
        self.longitude = new_lon
        self.altitude = new_alt

        #
        # LOOK-AHEAD TFR AVOIDANCE (WEEK 4)
        #
        if self.step_index + 1 < len(self.trajectory):
            next_row = self.trajectory.iloc[self.step_index + 1]
            next_lat = next_row["latitude"]
            next_lon = next_row["longitude"]

            if self.model.tfr.contains(next_lat, next_lon):
                print(f"🚫 {self.callsign} avoiding TFR")

                # simple deviation
                self.latitude += 0.1
                self.longitude += 0.1

                self.avoidance_count += 1

        # store trajectory
        self.history.append((self.latitude, self.longitude))

        print(f"{self.callsign} position: {self.latitude:.4f}, {self.longitude:.4f}")

        #
        # TFR VIOLATION CHECK
        #
        inside_tfr = self.model.tfr.contains(self.latitude, self.longitude)

        # cooldown update
        if self.tfr_cooldown > 0:
            self.tfr_cooldown -= 1

        # entry-based detection
        if inside_tfr and not self.in_tfr and self.tfr_cooldown == 0:
            print(f"⚠ WARNING: {self.callsign} ENTERED TFR!")
            self.violation_count += 1

            self.violation_points.append((
                self.longitude,
                self.latitude,
                self.altitude
            ))

            self.tfr_cooldown = 20

        self.in_tfr = inside_tfr

        self.step_index += 1