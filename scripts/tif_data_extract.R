#*******************************************************************************#
#                           CREST INPUTS PREPARATION                            #
#*******************************************************************************#
#*
#*NETOYAGE

rm(list = ls())


## LIBRARIES
library(sf)      
library(terra)   

## WORK SPACE
setwd("G:/CRA-AOS/EWS/EF5/CREST/CREST_BFA")


# Définition des chemins des fichiers
input_tif_dir <- "G:/CRA-AOS/MODELISATION/CREST/Ressources/EF5-Global-Parameters/5km/parameters"
input_tif_dir <- "F:/FEWSNET/all_tif_R"
input_tif_dir <- "G:/CRA-AOS/MODELISATION/CREST/Ressources/EF5-Global-Parameters/5km/parameters"
input_tif_dir <- "G:/CRA-AOS/MODELISATION/CREST/Ressources/EF5-Global-Parameters/FAO_PET"
input_tif_dir <- "G:/PROJET/Article/MODELISATION_II/EF5/EF5-INPERSON-TRAINING/model_repository/data/basic"
input_tif_dir <- "F:/chirps_clipped"
tif_files <- dir(path = input_tif_dir,pattern = "\\.tif$")
shp_file <- "gis/bf_subbasins_lev08_valid_extent.shp"  
ouput_tif_dir <- "data/precip"  # Chemin du raster découpé
# Charger le shapefile
shp <- st_read(shp_file)
#plot(shp)
# Fonction équivalente à clip_raster
clip_raster <- function(pathraster,shp_file,is.rasterPath=TRUE) {
  if(is.rasterPath){
    raster <- rast(pathraster)
  }else{
    raster <- pathraster
  }
  if(nchar(crs(raster))==0){
    crs(raster) <- "EPSG:4326"
  }
  shapefile <- shp_file#t_read(shp_file)
  shapefile <- st_transform(shapefile, crs(raster))
  raster_clipped <- crop(raster, vect(shapefile))         
  raster_clipped <- mask(raster_clipped, vect(shapefile)) 
  raster_clipped[is.na(raster_clipped)] <- -9999
  NAflag(raster_clipped) <- -9999
  crs(raster_clipped) <- "EPSG:4326"
  return(raster_clipped)
}

for (tif_file in tif_files) {
  dem_float32 <- clip_raster(file.path(input_tif_dir,tif_file),shp)
  out_tif_file <- tools::file_path_sans_ext(basename(tif_file))
  cat("\rRaster ", out_tif_file, " as been cliped successfully")
  flush.console()
  terra::writeRaster(dem_float32, file.path(ouput_tif_dir,paste0(out_tif_file,".tif")), datatype = "FLT4S", overwrite = TRUE, NAflag = -9999)
  
}

