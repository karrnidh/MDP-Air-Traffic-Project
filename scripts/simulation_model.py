from mesa import Model
from mesa.time import RandomActivation
from aircraft_agent import AircraftAgent
from tfr_zone import TFRZone
import pandas as pd
import sqlite3
import random


class AirTrafficModel(Model):

    def __init__(self):
        super().__init__()

        #
        # TFR ZONE
        #
        self.tfr = TFRZone(
            center_lat=25.997,
            center_lon=-97.156,
            radius_km=30
        )

        self.schedule = RandomActivation(self)

        #
        # SEPARATION TRACKING
        #
        self.separation_violations = {}
        self.active_violations = set()

        #
        # LOAD DATA FROM DATABASE
        #
        conn = sqlite3.connect("../air_traffic_zma_zhu.db")

        data = pd.read_sql(
            "SELECT * FROM Combined_Aircraft_Tracking",
            conn
        )

        conn.close()

        #
        # CLEAN DATA
        #
        data[['latitude', 'longitude']] = data['Position'].str.split(',', expand=True)
        data['latitude'] = data['latitude'].astype(float)
        data['longitude'] = data['longitude'].astype(float)

        #
        # GROUP BY AIRCRAFT
        #
        grouped = data.groupby("Callsign")
        flights = list(grouped.groups.keys())

        print(f"Total real aircraft: {len(flights)}")

        #
        # CREATE REAL + SYNTHETIC AGENTS
        #
        for flight in flights:

            flight_data = grouped.get_group(flight)

            if "Timestamp" in flight_data.columns:
                flight_data = flight_data.sort_values("Timestamp")

            # -------- REAL AGENT --------
            aircraft = AircraftAgent(
                model=self,
                callsign=flight,
                trajectory=flight_data
            )
            self.schedule.add(aircraft)

            # -------- SYNTHETIC AGENT --------
            synthetic_data = flight_data.copy()

            # realistic spatial shift (main fix)
            synthetic_data["latitude"] += synthetic_data["latitude"].apply(
                lambda _: random.uniform(-0.15, 0.15)
            )
            synthetic_data["longitude"] += synthetic_data["longitude"].apply(
                lambda _: random.uniform(-0.15, 0.15)
            )

            #trajectory variation (prevents identical paths)
            synthetic_data["latitude"] += synthetic_data.index.map(
                lambda _: random.uniform(-0.01, 0.01)
            )
            synthetic_data["longitude"] += synthetic_data.index.map(
                lambda _: random.uniform(-0.01, 0.01)
            )

            synthetic_callsign = flight + "_SYN"

            synthetic_aircraft = AircraftAgent(
                model=self,
                callsign=synthetic_callsign,
                trajectory=synthetic_data
            )

            self.schedule.add(synthetic_aircraft)

        print(f"Total agents (real + synthetic): {len(self.schedule.agents)}")

    #
    # SEPARATION CHECK (EVENT-BASED)
    #
    def check_separation(self):
        agents = self.schedule.agents
        new_active = set()

        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):

                a1 = agents[i]
                a2 = agents[j]

                if a1.latitude is None or a2.latitude is None:
                    continue

                # CRITICAL FIX — skip synthetic-self pairs
                if a1.callsign.replace("_SYN", "") == a2.callsign.replace("_SYN", ""):
                    continue

                # distance calculation (approx km)
                dlat = a1.latitude - a2.latitude
                dlon = a1.longitude - a2.longitude
                distance = ((dlat**2 + dlon**2) ** 0.5) * 111

                pair = tuple(sorted([a1.callsign, a2.callsign]))

                if distance < 5.56:  # 3 NM rule

                    new_active.add(pair)

                    # count only NEW violations
                    if pair not in self.active_violations:

                        print(f"⚠ SEPARATION EVENT: {pair[0]} & {pair[1]}")

                        self.separation_violations.setdefault(a1.callsign, 0)
                        self.separation_violations.setdefault(a2.callsign, 0)

                        self.separation_violations[a1.callsign] += 1
                        self.separation_violations[a2.callsign] += 1

        self.active_violations = new_active

    #
    # STEP
    #
    def step(self):
        self.schedule.step()
        self.check_separation()