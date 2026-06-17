import pandas as pd
import sys

files = [
    r"C:\QGIS\Mt Elvire - Copy\data\vectors\Easter_Field_mapping_points and comments.csv",
    r"C:\QGIS\Mt Elvire - Copy\data\vectors\Easter_Field_mapping_points and comments_MAY_update.xlsx",
]

for p in files:
    try:
        print("===", p)
        df = pd.read_csv(p) if p.endswith('.csv') else pd.read_excel(p)
        print("rows:", len(df))
        print("cols:", list(df.columns))
        print(df.head(2).to_string())
    except Exception as e:
        print(f"Error processing {p}: {e}")
