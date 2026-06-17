"""Copy field photos into a new tree using their Photo_ID as the filename.

Reads `photo_id_lookup.csv` (produced after the area-code update) and copies
every original photo to:

    <ROOT>\renamed\<Area_Code>\<Photo_ID>.<ext>

Originals are left untouched. A manifest CSV records every copy operation so
the renamed tree can be regenerated or reversed.
"""

import csv
import os
import shutil

ROOT = r"C:\QGIS\Mt Elvire - Copy\data\rasters\Field_mapping_photos"
LOOKUP = os.path.join(ROOT, "photo_id_lookup.csv")
OUT_DIR = os.path.join(ROOT, "renamed")
MANIFEST = os.path.join(ROOT, "photo_rename_manifest.csv")


def main():
    rows = []
    copied = skipped = missing = 0

    with open(LOOKUP, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            src = row["Full_path"].strip()
            pid = row["Photo_ID"].strip()
            area = (row["Area_Code"] or "GEN").strip()
            if not src or not pid:
                continue
            if not os.path.isfile(src):
                missing += 1
                rows.append({**row, "New_path": "", "Status": "missing_source"})
                continue

            ext = os.path.splitext(src)[1].lower() or ".jpg"
            dst_dir = os.path.join(OUT_DIR, area)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, f"{pid}{ext}")

            status = "copied"
            if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src):
                status = "skipped_existing"
                skipped += 1
            else:
                shutil.copy2(src, dst)
                copied += 1
            rows.append({**row, "New_path": dst, "Status": status})

    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        fieldnames = ["Photo_ID", "Site_ID", "Area_Code", "Area_Name",
                      "Original_filename", "Full_path", "New_path", "Status"]
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Copied: {copied} | already present (skipped): {skipped} | missing source: {missing}")
    print(f"Renamed tree: {OUT_DIR}")
    print(f"Manifest:     {MANIFEST}")


if __name__ == "__main__":
    main()
