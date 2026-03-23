from mesa import Model
from mesa.time import RandomActivation
from aircraft_agent import AircraftAgent
from tfr_zone import TFRZone
import pandas as pd
import sqlite3

class AirTrafficModel(Model):

    def __init__(self):
        super().__init__()

        # TFR zone (Starship example)
        self.tfr = TFRZone(
            center_lat=25.997,
            center_lon=-97.156,
            radius_km=30
        )

        self.schedule = RandomActivation(self)

        # =========================
        # LOAD DATA FROM DATABASE
        # =========================
        conn = sqlite3.connect("../air_traffic_zma_zhu.db")

        data = pd.read_sql(
            "SELECT * FROM Combined_Aircraft_Tracking",
            conn
        )

        conn.close()

        # =========================
        # CLEAN DATA
        # =========================
        data[['latitude','longitude']] = data['Position'].str.split(',', expand=True)
        data['latitude'] = data['latitude'].astype(float)
        data['longitude'] = data['longitude'].astype(float)

        # =========================
        # GROUP BY AIRCRAFT
        # =========================
        grouped = data.groupby("Callsign")

        flights = list(grouped.groups.keys())

        print(f"Total aircraft in DB: {len(flights)}")

        # pick first 5 aircraft
        selected_flights = flights[:5]

        print(f"Aircraft being simulated: {selected_flights}")

        # =========================
        # CREATE AGENTS
        # =========================
        for flight in selected_flights:

            flight_data = grouped.get_group(flight)

            # sort by time (IMPORTANT)
            if "Timestamp" in flight_data.columns:
                flight_data = flight_data.sort_values("Timestamp")

            aircraft = AircraftAgent(
                model=self,
                callsign=flight,
                trajectory=flight_data
            )

            self.schedule.add(aircraft)

        print(f"Agents created: {len(self.schedule.agents)}")

    def step(self):
        self.schedule.step()