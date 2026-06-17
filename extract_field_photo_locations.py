"""Extract GPS location + image direction from field-mapping photos.

Walks a fixed set of dated subfolders under the Field_mapping_photos root and
writes a single CSV containing one row per geotagged image:
    folder, filename, full_path, latitude, longitude, direction

`direction` is the EXIF GPSImgDirection in degrees (0 = North, clockwise). It
is left blank if the camera did not record a heading. The CSV is suitable for
loading directly into QGIS via the "Delimited Text" provider (WGS84).
"""

import csv
import os

import exifread

ROOT = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos"
SUBFOLDERS = ["02.04.26", "03.04.26", "04.04.26", "05.04.26", "06.06.26"]
OUT_CSV = os.path.join(ROOT, "field_photo_locations.csv")


def _ratio(r):
    return float(r.num) / float(r.den) if r.den else None


def _dms_to_deg(value):
    d, m, s = value.values
    return _ratio(d) + _ratio(m) / 60.0 + _ratio(s) / 3600.0


def extract(path):
    with open(path, "rb") as f:
        tags = exifread.process_file(f, details=False)
    lat = lon = direction = None
    try:
        lat = _dms_to_deg(tags["GPS GPSLatitude"])
        if str(tags["GPS GPSLatitudeRef"].values).strip().upper() != "N":
            lat = -lat
        lon = _dms_to_deg(tags["GPS GPSLongitude"])
        if str(tags["GPS GPSLongitudeRef"].values).strip().upper() != "E":
            lon = -lon
    except Exception:
        pass
    try:
        direction = _ratio(tags["GPS GPSImgDirection"].values[0])
    except Exception:
        pass
    return lat, lon, direction


def main():
    rows = []
    for sub in SUBFOLDERS:
        folder = os.path.join(ROOT, sub)
        if not os.path.isdir(folder):
            print(f"  ! missing folder: {folder}")
            continue
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            full = os.path.join(folder, name)
            lat, lon, direction = extract(full)
            if lat is None or lon is None:
                continue
            rows.append({
                "folder": sub,
                "filename": name,
                "full_path": full,
                "latitude": lat,
                "longitude": lon,
                "direction": "" if direction is None else round(direction, 2),
            })

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["folder", "filename", "full_path", "latitude", "longitude", "direction"],
        )
        w.writeheader()
        w.writerows(rows)

    with_dir = sum(1 for r in rows if r["direction"] != "")
    print(f"Wrote {len(rows)} rows ({with_dir} with direction) to {OUT_CSV}")


if __name__ == "__main__":
    main()
