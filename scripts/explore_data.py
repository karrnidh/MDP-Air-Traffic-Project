import pandas as pd

data = pd.read_csv("../Combined_Aircraft_Tracking.csv")

print("Columns:")
print(data.columns)

print("\nFirst rows:")
print(data.head())

data[['latitude','longitude']] = data['Position'].str.split(',', expand=True)

data['latitude'] = data['latitude'].astype(float)
data['longitude'] = data['longitude'].astype(float)

print("\nConverted coordinates:")
print(data[['latitude','longitude']].head())