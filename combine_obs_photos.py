import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# File paths
obs_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/Easter_Field_mapping_points and comments_MAY_update.xlsx'
photo_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/photo_coordinates_updated.csv'
out_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/combined_observations_photos.xlsx'

# Read data
obs_df = pd.read_excel(obs_path)
photo_df = pd.read_csv(photo_path)

# Clean column names (strip spaces)
photo_df.columns = photo_df.columns.str.strip()

# Use correct column names
obs_e = obs_df['UTM_Easting'].values
obs_n = obs_df['UTM_Northing'].values
photo_e = photo_df['UTM_EASTING'].values
photo_n = photo_df['UTM_NORTHING'].values

# Build KDTree for fast nearest neighbor search
photo_tree = cKDTree(np.c_[photo_e, photo_n])

# Find nearest photo for each observation (within 10 meters)
dist, idx = photo_tree.query(np.c_[obs_e, obs_n], distance_upper_bound=10)

# Mask out-of-bounds indices
valid = (idx < len(photo_df)) & (dist < 10)
photo_filenames = photo_df['FILE NAME '].values if 'FILE NAME ' in photo_df.columns else photo_df['FILE NAME'].values
image_names = photo_df['IMAGE NAME '].values if 'IMAGE NAME ' in photo_df.columns else photo_df['IMAGE NAME'].values
nearest_photo = np.full(len(obs_df), None, dtype=object)
nearest_image_name = np.full(len(obs_df), None, dtype=object)
photo_easting = np.full(len(obs_df), np.nan)
photo_northing = np.full(len(obs_df), np.nan)
photo_distance = np.full(len(obs_df), np.nan)
nearest_photo[valid] = photo_filenames[idx[valid]]
nearest_image_name[valid] = image_names[idx[valid]]
photo_easting[valid] = photo_e[idx[valid]]
photo_northing[valid] = photo_n[idx[valid]]
photo_distance[valid] = dist[valid]
obs_df['nearest_photo'] = nearest_photo
obs_df['nearest_image_name'] = nearest_image_name
obs_df['photo_easting'] = photo_easting
obs_df['photo_northing'] = photo_northing
obs_df['photo_distance_m'] = photo_distance

# Save to Excel
obs_df.to_excel(out_path, index=False)
print(f'Combined file written to {out_path}')
