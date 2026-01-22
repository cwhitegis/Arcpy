import arcpy
from arcgis import GIS
from arcgis.features._version import VersionManager

aprx = arcpy.mp.ArcGISProject('CURRENT')
mp = aprx.activeMap
mv = aprx.activeView
lyrs = mp.listLayers()
recordLyr = mp.listLayers('Records')[0]
pLinesUrl = 'https://portal.url/FeatureServer/'
arcpy.env.overwriteOutput = True
gis = GIS('pro')
user = gis.properties.user.username
arcpy.AddMessage(f'User Name: {user}')
mp.clearSelection()
outFcName = 'Deleted Parcel Lines'
#Access version
editVersion = recordLyr.connectionProperties['connection_info']['version']
arcpy.AddMessage(f'Edit Version: {editVersion}')

#Access version from the Version Manger Server
vms_url = f"https://portal.url/VersionManagementServer"
vms = VersionManager(vms_url, gis)
with vms.get(editVersion,"read") as version:
    diff = version.differences(result_type='objectIds',moment=None,layers=[17])

pLinesDelete = diff['differences'][0]['deletes']
arcpy.AddMessage(f"Parcel Lines Deleted: {len(pLinesDelete)}")

searchExp = f"objectid IN ({','.join(map(str, pLinesDelete))})"
#Create layer of Deleted Parcel Lines
plDeleteLyr = arcpy.management.MakeFeatureLayer(pLinesUrl,outFcName,where_clause = searchExp).getOutput(0)
mp.addLayer(plDeleteLyr)

deletedLines = mp.listLayers(outFcName)[0]
sym = deletedLines.symbology
sym.updateRenderer('SimpleRenderer')
deletedLines.symbology = sym
sym = deletedLines.symbology
sym.renderer.symbol.color = {'RGB':[255,0,0,100]}
sym.renderer.symbol.size = 3
deletedLines.symbology = sym
#mv.camera.setExtent(mv.getLayerExtent(deletedLines))
arcpy.AddMessage('Added Deleted Parcel Lines Layer to TOC for Review')

