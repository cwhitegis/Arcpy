import arcpy
from arcgis import GIS
from arcgis.features._version import VersionManager

aprx = arcpy.mp.ArcGISProject('CURRENT')
mp = aprx.activeMap
mv = aprx.activeView
lyrs = mp.listLayers()
recordLyr = mp.listLayers('Records')[0]
lyrList = []
lyrIDs = [1,2,3,4]
gis = GIS('pro')
user = gis.properties.user.username
arcpy.AddMessage(f'User Name: {user}')

#Access version GUID from the datasource
start = recordLyr.dataSource.find('{')
stop = recordLyr.dataSource.find('}') + 1
versionGUID = recordLyr.dataSource[start:stop]
arcpy.AddMessage(f'Edit Version GUID: {versionGUID}')

for lyr in lyrs:
    if lyr.isFeatureLayer:
        if 'Easements' == lyr.name or 'Easements_Lines' == lyr.name or 'Lots' == lyr.name or 'Condos' == lyr.name:
            lyrList.append(lyr)

#Access versions from the Version Manger Server
version_management_server_url = f"https://mysite.com/server/rest/services/VersionManagementServer"
vms = VersionManager(version_management_server_url, gis)
for v in vms.all:
    if v.properties.versionGuid == versionGUID:
        editVer = v
        arcpy.AddMessage(f'Found Edit Version {v}')
        break

#Reads the edit version and gets the differences
editVer.start_reading()
diff = editVer.differences(result_type='objectIds', moment=None, layers=lyrIDs)
editVer.stop_reading()

updateDict = {}
for dif in diff['differences']:
    for lyr in lyrList:
        if lyr.isFeatureLayer:
            if lyr.dataSource.endswith(f"/{dif['layerId']}"):
                if len(dif) == 2:
                    if 'inserts' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])})")
                        updateDict[lyr.name] = dif['inserts']
                    if 'updates' in dif:
                        arcpy.AddMessage(f"{lyr.name} Updates({len(dif['updates'])})")
                        updateDict[lyr.name] = dif['updates']
                    if 'deletes' in dif:
                        arcpy.AddMessage(f"{lyr.name} Deletes({len(dif['deletes'])})")
                if len(dif) == 3:
                    if 'inserts' in dif and 'updates' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Updates({len(dif['updates'])})")
                        updateDict[lyr.name] = dif['inserts']
                        updateDict[lyr.name] = dif['updates']
                    if 'inserts' in dif and 'deletes' in dif:
                        arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Deletes({len(dif['deletes'])})")
                        updateDict[lyr.name] = dif['inserts']
                    if 'updates' in diff and 'deletes' in dif:
                        arcpy.AddMessage(f"{lyr.name} Updates({len(dif['updates'])}),Deletes({len(dif['deletes'])})")
                        updateDict[lyr.name] = dif['updates']
                if len(dif) == 4:
                    arcpy.AddMessage(f"{lyr.name} Inserts({len(dif['inserts'])}),Updates({len(dif['updates'])}),Deletes({len(dif['deletes'])})")
                    updateDict[lyr.name] = dif['inserts']
                    updateDict[lyr.name] = dif['updates']

#Select features based on object ids for updates
for lyr in lyrList:
    for k, v in updateDict.items():
        if lyr.name == k:
            exp = f"objectid IN ({','.join(map(str,v))})"
            arcpy.management.SelectLayerByAttribute(lyr,'NEW_SELECTION',where_clause = exp)

#Zoom to selection
for lyr in lyrList:
    if lyr.getSelectionSet() is not None:
        mv.camera.setExtent(mv.getLayerExtent(lyr))






