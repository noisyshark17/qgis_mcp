import os
import exifread
import pandas as pd
from pyproj import Transformer

ROOT = r'C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos'
OUT = r'C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos\photo_coordinates_with_direction.csv'

def ratio_to_float(r):
    return float(r.num) / float(r.den) if r.den else None

def dms_to_deg(value):
    d, m, s = value.values
    return ratio_to_float(d) + ratio_to_float(m)/60 + ratio_to_float(s)/3600

def extract(path):
    with open(path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
    lat = lon = direction = direction_ref = None
    try:
        lat = dms_to_deg(tags['GPS GPSLatitude'])
        if tags['GPS GPSLatitudeRef'].values != 'N':
            lat = -lat
        lon = dms_to_deg(tags['GPS GPSLongitude'])
        if tags['GPS GPSLongitudeRef'].values != 'E':
            lon = -lon
    except Exception:
        pass
    try:
        d = tags['GPS GPSImgDirection'].values[0]
        direction = ratio_to_float(d)
        direction_ref = str(tags.get('GPS GPSImgDirectionRef', '')).strip()
    except Exception:
        pass
    return lat, lon, direction, direction_ref

rows = []
for subdir, _, files in os.walk(ROOT):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            p = os.path.join(subdir, f)
            lat, lon, direction, dref = extract(p)
            rows.append({
                'filename': os.path.relpath(p, ROOT),
                'image_name': f,
                'latitude': lat,
                'longitude': lon,
                'photo_direction_deg': direction,
                'photo_direction_ref': dref,
            })

df = pd.DataFrame(rows)
tr = Transformer.from_crs('EPSG:4326', 'EPSG:28350', always_xy=True)
def to_utm(r):
    if pd.notnull(r['latitude']) and pd.notnull(r['longitude']):
        e, n = tr.transform(r['longitude'], r['latitude'])
        return pd.Series({'UTM_Easting': e, 'UTM_Northing': n})
    return pd.Series({'UTM_Easting': None, 'UTM_Northing': None})
df[['UTM_Easting', 'UTM_Northing']] = df.apply(to_utm, axis=1)
df.to_csv(OUT, index=False)
print(f'Wrote {len(df)} rows to {OUT}')
print('With direction:', df['photo_direction_deg'].notna().sum())
print(df[df['photo_direction_deg'].notna()].head())
