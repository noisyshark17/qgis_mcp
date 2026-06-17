import os
import exifread
import pandas as pd
from pyproj import Transformer

def get_gps_coords(tags):
    try:
        gps_latitude = tags['GPS GPSLatitude']
        gps_latitude_ref = tags['GPS GPSLatitudeRef'].values
        gps_longitude = tags['GPS GPSLongitude']
        gps_longitude_ref = tags['GPS GPSLongitudeRef'].values
        
        def to_degrees(value):
            d, m, s = value.values
            return float(d.num)/float(d.den) + \
                   float(m.num)/float(m.den)/60 + \
                   float(s.num)/float(s.den)/3600
        
        lat = to_degrees(gps_latitude)
        if gps_latitude_ref != 'N':
            lat = -lat
        lon = to_degrees(gps_longitude)
        if gps_longitude_ref != 'E':
            lon = -lon
        return lat, lon
    except Exception:
        return None, None

def scan_photos(root_dir):
    photo_data = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(subdir, file)
                with open(path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    lat, lon = get_gps_coords(tags)
                photo_data.append({'filename': os.path.relpath(path, root_dir), 'latitude': lat, 'longitude': lon})
    return photo_data

def main():
    root = r'C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos'
    out_csv = r'C:\QGIS\Mt Elvire - Copy\photo_coordinates.csv'
    data = scan_photos(root)
    df = pd.DataFrame(data)
    # Transformer for EPSG:4326 to EPSG:28350
    transformer = Transformer.from_crs('EPSG:4326', 'EPSG:28350', always_xy=True)
    def to_utm(row):
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            e, n = transformer.transform(row['longitude'], row['latitude'])
            return pd.Series({'easting': e, 'northing': n})
        else:
            return pd.Series({'easting': None, 'northing': None})
    df[['easting', 'northing']] = df.apply(to_utm, axis=1)
    df.to_csv(out_csv, index=False)
    print(f'CSV updated with UTM coordinates at {out_csv}')

if __name__ == '__main__':
    main()
