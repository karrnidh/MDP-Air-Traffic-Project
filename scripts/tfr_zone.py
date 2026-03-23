import math

class TFRZone:

    def __init__(self, center_lat, center_lon, radius_km):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km

    def contains(self, lat, lon):

        dlat = lat - self.center_lat
        dlon = lon - self.center_lon

        distance = math.sqrt(dlat**2 + dlon**2) * 111

        return distance <= self.radius_km