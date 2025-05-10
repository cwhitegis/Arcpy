import arcpy
from arcgis import GIS

aprx = arcpy.mp.ArcGISProject('CURRENT')
mp = aprx.activeMap
mv = aprx.activeView
lyrs = mp.listLayers()
gis = GIS('pro')
user = gis.properties.user.username
arcpy.AddMessage(f'User Name: {user}')
lyrList = []

#Finds the versions GUID from the layer data source in the Map
for lyr in lyrs:
    if lyr.isFeatureLayer:
        if lyr.dataSource.endswith('/1'):
            start = lyr.dataSource.find('{')
            stop = lyr.dataSource.find('}') + 1
            versionGUID = lyr.dataSource[start:stop]
            arcpy.AddMessage(f'Edit Version GUID: {versionGUID}')
        if 'Easements' == lyr.name or 'Lots' == lyr.name or 'Condos' == lyr.name:
            lyrList.append(lyr)

#Finds the feature layer in feature service to final all versions in the container
items = gis.content.search("title: Parcel_Edits", item_type="Feature Layer")[0]
pfc = items.layers[0].container
verMgr = pfc.versions.all
for ver in verMgr:
    if ver.properties['versionGuid'] == versionGUID:
        editVer = ver
        arcpy.AddMessage(f"Found Version: {editVer.properties['versionGuid']}")
        break

#Reads the edit version and gets the differences
editVer.start_reading()
diff = editVer.differences(result_type='objectIds', moment=None)
editVer.stop_reading()

#loops through differences in the edit version
updateDict = {}
for dif in diff['differences']:
    for lyr in lyrList:
        if lyr.isFeatureLayer:
            if lyr.dataSource.endswith(f"/{dif['layerId']}"):
                if len(dif) == 2:
                    if 'inserts' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])})")
                    if 'updates' in dif:
                        arcpy.AddMessage(f"{lyr.name} Updates({len(dif['updates'])})")
                        updateDict[lyr.name] = dif['updates']
                    else:
                        arcpy.AddMessage(f"{lyr.name} Deletes({len(dif['deletes'])})")
                if len(dif) == 3:
                    if 'inserts' in dif and 'updates' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Updates({len(dif['updates'])})")
                        updateDict[lyr.name] = dif['updates']
                    if 'inserts' in dif and 'deletes' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Deletes({len(dif['deletes'])})")
                        updateDict[lyr.name] = dif['updates']
                    if 'updates' in diff and 'deletes' in dif:
                        arcpy.AddMessage(f"{lyr.name} Updates({len(dif['updates'])}),Deletes({len(dif['deletes'])})")
                        updateDict[lyr.name] = dif['updates']
                if len(dif) == 4:
                    arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Updates({len(dif['updates'])}),Deletes({len(dif['deletes'])})")
                    updateDict[lyr.name] = dif['updates']
#Select based on object ids for updates
for lyr in lyrList:
    for k, v in updateDict.items():
        if lyr.name == k:
            exp = f"objectid IN ({','.join(map(str,v))})"
            arcpy.management.SelectLayerByAttribute(lyr,'NEW_SELECTION',where_clause = exp)
#Zoom to selection
for lyr in lyrList:
    if lyr.getSelectionSet() is not None:
        mv.camera.setExtent(mv.getLayerExtent(lyr))






