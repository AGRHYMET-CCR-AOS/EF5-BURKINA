import rasterio
import geopandas as gpd
from rasterio.features import geometry_mask
import numpy as np
import os
from shapely.geometry import Point
#os.environ['PROJ_LIB'] = r'C:\ProgramData\anaconda3\envs\crest_data_preparation\Library\share\proj'

os.chdir('G:/CRA-AOS/EWS/EF5/CREST/CREST_BFA/')
savePath="data_preparation"
if not os.path.exists(savePath) :
    os.makedirs(savePath,exist_ok=True)
# === Chargement du shapefile ===
shapefile_path = "G:/CRA-AOS/EWS/EF5/CREST/CREST_BFA/gis/bfa_subbassins2.shp"
if not os.path.exists(shapefile_path):
    raise FileNotFoundError(f"Aucun fichier {shapefile_path} n'existe")

gdf = gpd.read_file(shapefile_path)
gdf.plot()
print("CRS des points :", gdf.crs)
gdf.columns


# === Création de géométries ponctuelles à partir de POURX (lon) et POURY (lat) ===
gdf["geometry"] = [Point(xy) for xy in zip(gdf["POURX"], gdf["POURY"])]
gdf.set_geometry("geometry", inplace=True)
gdf.set_crs(epsg=4326, inplace=True)


raster_path ="data/basic/fam.tif"
# === Ouverture du raster ===
with rasterio.open(raster_path) as src:
    raster_crs = src.crs

    # Reprojection vers le CRS du raster
    if gdf.crs != raster_crs:
        print("Reprojection des points vers le CRS du raster...")
        gdf = gdf.to_crs(raster_crs)

    # Conversion géométrie en coordonnées
    coords = [(geom.x, geom.y) for geom in gdf.geometry]

    # Récupération des indices (row, col)
    rows_cols = [src.index(x, y) for x, y in coords]
    gdf["row"] = [r for r, c in rows_cols]
    gdf["col"] = [c for r, c in rows_cols]

    # Facultatif : lecture des valeurs du raster à ces points
    band = src.read(1)
    gdf["valeur_raster"] = [band[r, c] for r, c in rows_cols]

# === Résultat final ===
print(gdf[["SUBID", "row", "col", "valeur_raster"]].head())

with open(os.path.join(savePath,"gauges.txt"),"w") as f:
    ids = []
    i=0
    for id, row, col,ras_val in zip(gdf["SUBID"],gdf["row"],gdf["col"],gdf["valeur_raster"]):   
        i+=1
        if i != 1 :
            if id in ids:
                continue
        ids.append(id)        
        f.write(f"[Gauge {int(id)}] cellx={int(col)} celly={int(row)}  outputts=false #Num Cells = {int(ras_val)}\n")




with open(os.path.join(savePath,"basins.txt"),"w") as f:
    ids = []
    i=0
    for id in gdf["SUBID"]:  
        i+=1
        if i != 1 :
            if id in ids:
                continue
        ids.append(id) 
        f.write(f"gauge={int(id)} ")



