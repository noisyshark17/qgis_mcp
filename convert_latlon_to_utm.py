import pandas as pd
from pyproj import Transformer

# File paths
input_csv = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos\ss\field_photo_locations.csv"
output_csv = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos\ss\field_photo_locations_utm.csv"

# Read CSV
df = pd.read_csv(input_csv)

# Set up transformer: WGS84 to GDA94 / MGA zone 51 (EPSG:28351)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:28351", always_xy=True)

# Convert coordinates
def to_utm(row):
    easting, northing = transformer.transform(row['longitude'], row['latitude'])
    return pd.Series({'easting': easting, 'northing': northing})

df[['easting', 'northing']] = df.apply(to_utm, axis=1)

# Write to new CSV
df.to_csv(output_csv, index=False)

print("Conversion complete. Output saved to:", output_csv)
