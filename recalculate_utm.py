import pandas as pd
from pyproj import Transformer

# File paths
excel_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/combined_observations_photos.xlsx'
out_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/combined_observations_photos_recalculated.xlsx'

# Read data
obs_df = pd.read_excel(excel_path)

# Set up transformer for GDA94 / MGA zone 50 (EPSG:28350)
transformer = Transformer.from_crs('EPSG:4326', 'EPSG:28350', always_xy=True)

# Recalculate UTM for specified rows (178 to 193, 0-based index)
for idx in range(177, 194):
    lat = obs_df.at[idx, 'Latitude']
    lon = obs_df.at[idx, 'Longitude']
    if pd.notnull(lat) and pd.notnull(lon):
        e, n = transformer.transform(lon, lat)
        obs_df.at[idx, 'UTM_Easting'] = e
        obs_df.at[idx, 'UTM_Northing'] = n

# Save to new Excel file
obs_df.to_excel(out_path, index=False)
print(f'Recalculated UTM values for rows 178-193 and saved to {out_path}')
