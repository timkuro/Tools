# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Mosaik_Skript.py
# Created on: 2019-07-09 10:47:30.00000
#
# Usage: Mosaik_Skript <File_GDB_Name> 
# Description:
# A connection to ArcGIS Server must be established in the Catalog window of ArcMap
# before running this script
# Folder for saving of server connection file --> outdirServerCon MUST BE DEFINED
# username and password for ServerConnection MUST BE DEFINED
# Workspace ("Folder for Created FileGDB and Mosaic Datasets") MUST BE DEFINED
# product_results_path ("Connection to Folder containing TIF DataResultProducts") MUST BE DEFINED
# processed_prod_path  MUST BE DEFINED
# ---------------------------------------------------------------------------

# Set the necessary product code
import arceditor

# Import modules
import arcpy
import sys
import os
import fnmatch

arcpy.env.overwriteOutput = True
arcpy.CheckProduct('ArcInfo')


# Local variables:
outdirServerCon = "Folder for saving of server connection file"
out_folder_path = outdirServerCon
out_name = 'wacodisService.ags'
server_url = 'https://gis.wacodis.demo.52north.org:6443/arcgis/admin'
use_arcgis_desktop_staging_folder = True
username = 'admin'
password = 'admin'
con = os.path.join(outdirServerCon, out_name)
workspace = "Folder for Created FileGDB and Mosaic Datasets"
workspace_gdb = workspace
product_results_path = "Connection to Folder containing TIF DataResultProducts"
processed_prod_path = "Folder to mark Data Products as processed"
product_results_list = fnmatch.filter(os.listdir(product_results_path), "*.tif")
prod_list = []
date_list = []


try:
    for prod in product_results_list:
        product_name = prod.split('_')[1]
        date_list.append(prod.split('_')[2].split('.')[0])
        if product_name not in prod_list:
            prod_list.append(product_name)

    for gdb_name in prod_list:
        # Process: File-Geodatabase erstellen
        if arcpy.Exists(workspace_gdb+"\\"+gdb_name+".gdb"):
            print "GDB " + gdb_name + " exists"
            # Do nothing
        else:
            arcpy.CreateFileGDB_management(workspace_gdb, gdb_name)
        # Create Master Mosaic
        # Process: Mosaik-Dataset erstellen
            arcpy.CreateMosaicDataset_management(workspace_gdb+"\\" + gdb_name + '.gdb', "Master" + '_' + gdb_name,
                                                 "PROJCS['ETRS_1989_UTM_Zone_32N',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137.0,298.257222101]],"
                                                 "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],"
                                                 "PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',9.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],"
                                                 "UNIT['Meter',1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;IsHighPrecision")
            print "Created Master Mosaic for " + gdb_name

    # Create MosaicDataset for every processed Rasterproduct
    # Add the belonging Rasterfile(TIF) to the created MosaicDataset
    for prod_name in product_results_list:
        mosaic_prod = prod_name.split('_')[1].split('_')[0]
        mosaic_dataset_Name = prod_name[:len(prod_name)-4]+'_Mosaic'
        mosaic_product_name = "T" + mosaic_dataset_Name.replace("-", "_")
        for gdb_name in prod_list:
            if gdb_name in mosaic_prod:
                gdb_ws_name = gdb_name + '.gdb'
                # Process: Mosaik-Dataset erstellen
                arcpy.CreateMosaicDataset_management(workspace_gdb+"\\"+gdb_ws_name, mosaic_product_name, "PROJCS['ETRS_1989_UTM_Zone_32N', "
                                                                                                          "GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137.0,298.257222101]],"
                                                                                                          "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],"
                                                                                                          "PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],"
                                                                                                          "PARAMETER['Central_Meridian',9.0],"
                                                                                                          "PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],"
                                                                                                          "UNIT['Meter',1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;"
                                                                                                          "IsHighPrecision")
                print "Created Mosaic for " + gdb_ws_name + " with " + mosaic_product_name
                # Raster zum Mosaik hinzufügen
                arcpy.AddRastersToMosaicDataset_management(workspace_gdb+"\\"+gdb_ws_name + '\\' + mosaic_product_name, "Raster Dataset", product_results_path + "\\" + prod_name,
                                                           "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "UPDATE_OVERVIEWS", "", "0", "1500", "", "#", "SUBFOLDERS",
                                                           "EXCLUDE_DUPLICATES", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", "")
                print "Added Raster to Mosaic"
                # Process: Raster zu Mosaik-Dataset hinzufügen (add all belonging rasters to the Master Mosaic)
                arcpy.AddRastersToMosaicDataset_management(workspace_gdb+"\\"+gdb_ws_name + '\\' + "Master" + '_' + gdb_name, "Raster Dataset",
                                                           workspace_gdb + "\\" + gdb_ws_name + "\\" + mosaic_product_name,
                                                           "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "#", "NO_SUBFOLDERS", "EXCLUDE_DUPLICATES",
                                                           "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", "")
                print "Added Raster to MasterMosaic"
                # To DO mark processed datasets and save to another directory
                # os.rename(os.path.join(product_results_path,prod_name), os.path.join(processed_prod_path, prod_name))
except Exceptions:
    e = sys.exc_info()[1]
    print(e.args[0])
    print arcpy.GetMessages() + "\n\n"
    sys.exit("Failed in authoring mosaic datasets")

codeblock = """
def getYearQuat(date,dat):
    switcher = {
            "Fruehling": '-03',
            "Sommer": '-06',
            "Herbst": '-09',
            "Winter": '-12',
            }
    return date+switcher.get(dat, "-"+dat)
    """

try:
    print "Add and Calculate Fields"
    for gdb_name in prod_list:
        if len(arcpy.ListFields(workspace_gdb+"\\"+gdb_name + '.gdb\\' + 'Master' + "_" + gdb_name, "year_quat")) > 0:
            print "Field exists"
        else:
            print "Field doesn't exist"
            arcpy.AddField_management(workspace_gdb+"\\"+gdb_name + '.gdb\\' + 'Master' + "_" + gdb_name, "year_quat", "text")
            print "Added field"
        print arcpy.GetCount_management(workspace_gdb+"\\"+gdb_name + '.gdb\\' + 'Master' + "_" + gdb_name)
        arcpy.CalculateField_management(workspace_gdb+"\\"+gdb_name + '.gdb\\' + 'Master' + "_" + gdb_name, "year_quat",
                                        "getYearQuat(!NAME!.split('_')[2],!NAME!.split('_')[3])",
                                        "PYTHON", codeblock)
        print "Calculated Fields for " + gdb_name

except arcpy.ExecuteError:
    e = sys.exc_info()[1]
    print(e.args[0])
    print arcpy.GetMessages() + "\n\n"
    sys.exit("Failed in adding fields")

# make sure the folder is registered with the server, if not, add it to the datastore
#
# TO DO if Service exists and only new Mosaics should be updated --> update Service
#
# Create service definition draft
try:
    print "Creating Server Connection File"
    arcpy.mapping.CreateGISServerConnectionFile("PUBLISH_GIS_SERVICES",
                                                out_folder_path,
                                                out_name,
                                                server_url,
                                                "ARCGIS_SERVER",
                                                use_arcgis_desktop_staging_folder,
                                                None,
                                                username,
                                                password,
                                                "SAVE_USERNAME")
    print "Creating SD draft"
    for name in prod_list:
        if out_folder_path not in [i[2] for i in arcpy.ListDataStoreItems(con, 'FOLDER')]:
            # both the client and server paths are the same
            dsStatus = arcpy.AddDataStoreItem(con, "FOLDER", "Workspace for " + name + 'Service', out_folder_path, out_folder_path)
            print "Data store : " + str(dsStatus)
        Sddraft = os.path.join(workspace_gdb, name+"Service"+".sddraft")  # Name = Name der Bilddateien/ Ordner bzw. des sddraft
        arcpy.CreateImageSDDraft(os.path.join(workspace_gdb, name+'.gdb\\Master_'+name), Sddraft, name+"Service", 'ARCGIS_SERVER', None, False, 'WaCoDiS', name, name+",image service, WaCoDiS")
except arcpy.ExecuteError:
    e = sys.exc_info()[1]
    print(e.args[0])
    print arcpy.GetMessages() + "\n\n"
    sys.exit("Failed in creating SD draft")

# Analyze the service definition draft
for name in prod_list:
    Sddraft = os.path.join(workspace_gdb, name+"Service"+".sddraft")
    Sd = os.path.join(workspace_gdb, name+"Service"+".sd")
    analysis = arcpy.mapping.AnalyzeForSD(Sddraft)
    print "The following information was returned during analysis of the image service:"
    for key in ('messages', 'warnings', 'errors'):
        print '----' + key.upper() + '---'
        vars = analysis[key]
        for ((message, code), layerlist) in vars.iteritems():
            print '    ', message, ' (CODE %i)' % code
            print '       applies to:',
            for layer in layerlist:
                print layer.name,
            print
        # Stage and upload the service if the sddraft analysis did not contain errors
    if analysis['errors'] == {}:
        try:
            print "Staging service to create service definition"
            arcpy.StageService_server(Sddraft, Sd)

            print "Uploading the service definition and publishing image service"
            arcpy.UploadServiceDefinition_server(Sd, con)

            print "Service successfully published"
        except arcpy.ExecuteError:
            e = sys.exc_info()[1]
            print(e.args[0])
            print arcpy.GetMessages() + "\n\n"
            sys.exit("Failed to stage and upload service")
    else:
        print "Service could not be published because errors were found during analysis."
        print arcpy.GetMessages()


