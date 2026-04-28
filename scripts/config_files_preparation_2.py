import rasterio
import numpy as np
import os
import glob
os.chdir('G:/PROJET/Article/HYDRO_ML/Modeling/CREST/Mouhoun/')
# === Chemin d'entrée et de sortie ===
input_tif = "data/parameters/Global/soil_param_wm_5km_global.tif"
tif_files = glob.glob("data/parameters/Global/*.tif")
input_tif = tif_files[0]

base_dir = "data/parameters/Global/normalize"
for input_tif in tif_files:
    output_tif = os.path.join(base_dir,os.path.basename(input_tif))

    # === Ouverture du raster ===
    with rasterio.open(input_tif) as src:
        profile = src.profile
        data = src.read(1).astype(np.float32)  # lecture bande 1 en float32
        nodata = src.nodata

        # === Masquage des nodata (si défini)
        if nodata is not None:
            mask = data != nodata
            min_val = np.nanmin(data[mask])
            max_val = np.nanmax(data[mask])
            print(f"Min : {min_val}, Max : {max_val}")
            data[mask] = (data[mask] - min_val) / (max_val - min_val)
            data[~mask] = nodata  # restaurer les nodata
        else:
            min_val = np.nanmin(data)
            max_val = np.nanmax(data)
            print(f"Min : {min_val}, Max : {max_val}")
            data = (data - min_val) / (max_val - min_val)

        # === Mise à jour du profil
        profile.update(
            dtype=rasterio.float32,
            nodata=nodata
        )

        # === Écriture du raster normalisé
        with rasterio.open(output_tif, "w", **profile) as dst:
            dst.write(data, 1)

    print(f"✅ Fichier normalisé écrit : {output_tif}")
