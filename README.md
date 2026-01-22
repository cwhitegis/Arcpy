# Arcpy
## Arcpy Python Scripts
### WriteDictToCSV
#### This is a script to put one field as the key and have to list values. In my case I used it for parcel owner as the key. The two list values were parcels owned and acres of parcel. The output is one owner, parcel count, and sum of acers.

### APIDataCreateLayer
#### Gets data from alert west api and creates a feature layer from the lat long

### VersionDifferences
#### Uses the Arcgis API for Python to access version differences tool for feature service editing to select any updates or inserts made to layers

### DeletedParcelLines
#### Use with Parcel Fabric to retrive any deleted lines in an edit version from the default feature serivce. Accessing the version differences to find the objectIDs of deleted lines. Makes a feature layer from the objectIDs and adds it to the map. Lines can be copied into edit version parcel lines.
