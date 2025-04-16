import requests
import datetime
import csv
import arcpy

today = datetime.date.today()
formatted_date = today.strftime("%Y/%m/%d")
date_string = today.strftime("%m%d%Y")

#API URL Getting Data from AlertWest Cams
url = 'https://api.cdn.prod.alertwest.com/api/getCameraDataByLoc'
response = requests.request("GET", url)
data = response.json()['data']
#Create List of Data from API
locs = list(filter(lambda x: x['st'] == 'HI', data['locs']['data']))
loc_ids = list(map(lambda x: x['id'], locs))
cams = list(filter(lambda x: x['lid'] in loc_ids, data['cams']['data']))
#Set Variable to run in Arcgis Pro. Change to run stand alone
aprx = arcpy.mp.ArcGISProject("CURRENT")
mp = aprx.activeMap
lyrs= mp.listLayers()
arcpy.env.workspace = r"E:\ProProject\Default.gdb"
filename = f'C:\filenamepath\new_{date_string}.csv'
#Add key to cams list and change some
new_cam = []
for cam in cams:
    items = list(cam.items())
    items.insert(17,('isp',None))
    cam = dict(items)
    cam['cid'] = cam.pop('id')
    cam['camst'] = cam.pop('st')
    new_cam.append(cam)
#Merge the 2 dictionaries. Add couple Key:Values into one list for the feature class data
items = []
for loc in locs:
    for cam in new_cam:
        if loc['id'] == cam['lid']:
            new_dict = {}
            new_dict = {**loc,**cam}
            cid = new_dict['cid']
            imgfile = new_dict['img']
            new_dict['imgURL'] = f'https://img.cdn.prod.alertwest.com/data/img/{cid}/{formatted_date}/{imgfile}'
            new_dict['panoURL'] = f"https://alertwest.live/sapi/panoCropper/request?camid={cid}&azimuth={new_dict['p']}"
            items.append(new_dict)
#Write to CSV
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(items[0].keys())
    for item in items:
        writer.writerow(item.values())
#Create layer using lat long from data
ofc = f'outputfc_{date_string}'
arcpy.management.XYTableToPoint(
    in_table=filename,
    out_feature_class=ofc,
    x_field="lon",
    y_field="lat",
    z_field=None
    #WGS1984 is default coordinate system
    #coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
)

mp.addDataFromPath(r'E:\path\to\your\file')
print(f'CSV file "{filename}" created successfully.')