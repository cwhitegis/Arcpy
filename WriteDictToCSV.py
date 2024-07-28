import arcpy
import csv

aprx = arcpy.mp.ArcGISProject(r"C:\ProjectLocation\Test\Test.aprx")
mp = aprx.listMaps('Map_Name')[0]
lyr = mp.listLayers('Layer_Name')[0]

ownerDict = {}
fields = ['field1','field2', 'field3']

with arcpy.da.SearchCursor(lyr,fields) as cursor:
    for row in cursor:
        if row[0] not in ownerDict.keys() and row[1] is not None:
            ownerDict[row[0]] = [[row[1]],[row[2]]]
        else:
            if row[1] is not None:
                if row[1] not in ownerDict[row[0]][0]:
                        ownerDict[row[0]][0].append(row[1])
                        ownerDict[row[0]][1].append(row[2])

file = open(r"C:\Users\Documents\CSV_Location.csv", 'w', newline='')

with file as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['field1','field2', 'field3'])
    for k, v in ownerDict.items():
        #Write CSV with field 1,the length of field 2, and sum field 3 rounded to 2 decimals
        writer.writerow([k, len(v[0]),round(sum(v[1]),2)])

print('Done')
