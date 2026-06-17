"""Link field photos to Easter field-mapping observation points.

Reads the observation CSV (lat/lon in WGS84) and the photo CSV produced by
extract_field_photo_locations.py, projects both to the project CRS
(EPSG:28351, MGA94 zone 51), and for every observation finds the photos
within a search radius. Produces:

  * observations_with_photos.csv  — flat table for the report
  * observations_with_photos.gpkg — point layer for QGIS

Each observation gets a stable Site_ID ("FM-001", "FM-002", ...) so the
field-photo points on the map and the rows in the report table can be
cross-referenced at a glance.
"""

import os
import re

import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree

OBS_CSV = r"C:\QGIS\Mt Elvire - Copy\data\vectors\Easter_Field_mapping_points and comments.csv"
PHOTO_CSV = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos\field_photo_locations.csv"
OUT_DIR = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos"
OUT_CSV = os.path.join(OUT_DIR, "observations_with_photos.csv")
OUT_GPKG = os.path.join(OUT_DIR, "observations_with_photos.gpkg")
GPKG_LAYER = "observations_with_photos"

SEARCH_RADIUS_M = 5       # photos within this many metres of an observation are linked
MAX_PHOTOS_PER_OBS = 6    # cap on filenames stored per row


def main():
    obs = pd.read_csv(OBS_CSV)
    obs.columns = [c.strip() for c in obs.columns]
    obs = obs.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)

    # Stable Site_ID ordered by date then time
    def parse_dt(r):
        return pd.to_datetime(
            f"{r['Date']} {r['Time_UTC']}", dayfirst=True, errors="coerce"
        )
    obs["_dt"] = obs.apply(parse_dt, axis=1)
    obs = obs.sort_values(["_dt", "Latitude"], na_position="last").reset_index(drop=True)
    obs["Site_ID"] = [f"FM-{i + 1:03d}" for i in range(len(obs))]

    photos = pd.read_csv(PHOTO_CSV)
    photos = photos.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

    tr = Transformer.from_crs("EPSG:4326", "EPSG:28351", always_xy=True)
    obs[["E", "N"]] = obs.apply(
        lambda r: pd.Series(tr.transform(r["Longitude"], r["Latitude"])), axis=1
    )
    photos[["E", "N"]] = photos.apply(
        lambda r: pd.Series(tr.transform(r["longitude"], r["latitude"])), axis=1
    )

    tree = cKDTree(photos[["E", "N"]].values)
    matched_files = []
    matched_paths = []
    matched_count = []
    nearest_dist = []
    for _, r in obs.iterrows():
        idxs = tree.query_ball_point([r["E"], r["N"]], r=SEARCH_RADIUS_M)
        if not idxs:
            # also record nearest distance for diagnostics
            d, _ = tree.query([r["E"], r["N"]], k=1)
            matched_files.append("")
            matched_paths.append("")
            matched_count.append(0)
            nearest_dist.append(round(float(d), 1))
            continue
        # order matches by distance
        d2 = ((photos.loc[idxs, "E"].values - r["E"]) ** 2 +
              (photos.loc[idxs, "N"].values - r["N"]) ** 2)
        order = d2.argsort()
        idxs = [idxs[i] for i in order][:MAX_PHOTOS_PER_OBS]
        files = photos.loc[idxs, "filename"].tolist()
        paths = photos.loc[idxs, "full_path"].tolist()
        matched_files.append("; ".join(files))
        matched_paths.append("|".join(paths))
        matched_count.append(len(idxs))
        nearest_dist.append(round(float(d2[order[0]]) ** 0.5, 1))

    obs["Photo_count"] = matched_count
    obs["Photo_files"] = matched_files
    obs["Photo_paths"] = matched_paths
    obs["Nearest_photo_m"] = nearest_dist

    # Slim, report-friendly column order
    keep = [
        "Site_ID", "Date", "Time_UTC", "Name",
        "Latitude", "Longitude", "E", "N", "Elevation_m",
        "Dip", "Dip Direction", "Trend", "Description",
        "Photo_count", "Photo_files", "Photo_paths", "Nearest_photo_m",
    ]
    for c in keep:
        if c not in obs.columns:
            obs[c] = ""
    table = obs[keep].copy()
    table.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # Write GeoPackage via OGR (no Fiona dependency)
    try:
        from osgeo import ogr, osr
    except ImportError:
        print("osgeo not available — CSV written, skipping GPKG.")
        print(f"  CSV: {OUT_CSV}  ({len(table)} rows)")
        return

    if os.path.exists(OUT_GPKG):
        os.remove(OUT_GPKG)
    drv = ogr.GetDriverByName("GPKG")
    ds = drv.CreateDataSource(OUT_GPKG)
    srs = osr.SpatialReference(); srs.ImportFromEPSG(28351)
    lyr = ds.CreateLayer(GPKG_LAYER, srs, ogr.wkbPoint)

    field_defs = [
        ("Site_ID", ogr.OFTString, 16),
        ("Date", ogr.OFTString, 32),
        ("Time_UTC", ogr.OFTString, 16),
        ("Name", ogr.OFTString, 254),
        ("Description", ogr.OFTString, 1024),
        ("Dip", ogr.OFTReal, 0),
        ("Dip_Dir", ogr.OFTReal, 0),
        ("Trend", ogr.OFTReal, 0),
        ("Elevation_m", ogr.OFTReal, 0),
        ("Photo_count", ogr.OFTInteger, 0),
        ("Photo_files", ogr.OFTString, 2000),
        ("Photo_paths", ogr.OFTString, 4000),
        ("Nearest_photo_m", ogr.OFTReal, 0),
    ]
    for name, typ, width in field_defs:
        fd = ogr.FieldDefn(name, typ)
        if width:
            fd.SetWidth(width)
        lyr.CreateField(fd)

    def num(v):
        try:
            x = float(v)
            return None if pd.isna(x) else x
        except Exception:
            return None

    for _, r in obs.iterrows():
        feat = ogr.Feature(lyr.GetLayerDefn())
        feat.SetField("Site_ID", str(r["Site_ID"]))
        feat.SetField("Date", "" if pd.isna(r.get("Date")) else str(r.get("Date")))
        feat.SetField("Time_UTC", "" if pd.isna(r.get("Time_UTC")) else str(r.get("Time_UTC")))
        feat.SetField("Name", "" if pd.isna(r.get("Name")) else str(r.get("Name")))
        feat.SetField("Description", "" if pd.isna(r.get("Description")) else str(r.get("Description")))
        for src, dst in [("Dip", "Dip"), ("Dip Direction", "Dip_Dir"),
                         ("Trend", "Trend"), ("Elevation_m", "Elevation_m")]:
            v = num(r.get(src))
            if v is not None:
                feat.SetField(dst, v)
        feat.SetField("Photo_count", int(r["Photo_count"]))
        feat.SetField("Photo_files", r["Photo_files"])
        feat.SetField("Photo_paths", r["Photo_paths"])
        feat.SetField("Nearest_photo_m", float(r["Nearest_photo_m"]))
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint(float(r["E"]), float(r["N"]))
        feat.SetGeometry(pt)
        lyr.CreateFeature(feat)
        feat = None
    ds = None

    matched = (table["Photo_count"] > 0).sum()
    print(f"Observations: {len(table)} | with >=1 photo within {SEARCH_RADIUS_M} m: {matched}")
    print(f"CSV  -> {OUT_CSV}")
    print(f"GPKG -> {OUT_GPKG} (layer: {GPKG_LAYER}, CRS: EPSG:28351)")


if __name__ == "__main__":
    main()
