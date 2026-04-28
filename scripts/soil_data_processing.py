# %%
import rasterio
from rasterio.merge import merge
import glob
import os
import numpy as np
# %%
os.chdir("G:/CRA-AOS/MODELISATION/CREST/SoilParameters/soilgrids_clean")
# Lister les .tif à mosaïquer

layers = {
    "clay": ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"],
    "sand": ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"],
}
#%%
for variable, depths in layers.items():
    k=0
    for depth in depths:
         k+=1
         filename = f"{variable}_{depth}".replace("-", "m")
         tif_files = glob.glob(f"G:/CRA-AOS/MODELISATION/CREST/SoilParameters/soilgrids_downloads/{filename}*.tif")
        # Charger les rasters
         src_files_to_mosaic = [rasterio.open(fp) for fp in tif_files]
        # Mosaïque
         mosaic, out_trans = merge(src_files_to_mosaic)

        # Métadonnées de base
         out_meta = src_files_to_mosaic[0].meta.copy()

         out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
         })

         # Enregistrement
         if variable == 'clay':
             basename='_CLYPPT_M_sl'
         else:
             basename = '_SNDPPT_M_sl'
         with rasterio.open(f"inputs/BFA{basename}{k}_250m.tif", "w", **out_meta) as dest:
            dest.write(mosaic)

# %%
# === Chemin des rasters par profondeur ===
prefix = "BFA_CLYPPT_M_sl"  # Exemple pour % d'argile
suffix = "_250m.tif"
weights = [5, 10, 15, 30, 40, 100]  # épaisseurs de sl1 à sl6 (somme = 200)

#%%
layers = []
for i in range(1, 7):
    fname = f"inputs/{prefix}{i}{suffix}"
    with rasterio.open(fname) as src:
        data = src.read(1).astype('float32')  
        data[data == src.nodata] = np.nan    
        layers.append(data * weights[i-1])

# === Agrégation pondérée ===
weighted_sum = np.nansum(layers, axis=0)
sl7 = weighted_sum / sum(weights)

# === Sauvegarde du fichier agrégé sl7 ===
with rasterio.open(f"inputs/{prefix}1{suffix}") as src:
    meta = src.meta.copy()

meta.update({
    "dtype": 'float32',
    "nodata": -9999
})

sl7[np.isnan(sl7)] = -9999

with rasterio.open(f"inputs/{prefix}7{suffix}", "w", **meta) as dst:
    dst.write(sl7, 1)

print(f"✅ Fichier généré : {prefix}7{suffix}")

# %%
