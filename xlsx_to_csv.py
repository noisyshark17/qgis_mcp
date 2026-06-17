import pandas as pd

excel_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/combined_observations_photos_recalculated.xlsx'
csv_path = r'C:/QGIS/Mt Elvire - Copy/data/rasters/Field_mapping_photos/combined_observations_photos_recalculated.csv'

df = pd.read_excel(excel_path)
df.to_csv(csv_path, index=False)
print(f'Converted to {csv_path}')
