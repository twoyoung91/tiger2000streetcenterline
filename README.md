# tiger2000streetcenterline
This project is developed for converting the street centerlines from US Census Bureau tiger 2000 report files to shapefiles. The original format cannot be easily read by GIS software, and is separted by counties. 
The python script has three functions:
1. Automatically download tiger 2000 files from US Census bureau websites and extract the packages
2. Read road centerline records (record types start with "A") from the report files, convert them to GeoPandas Dataframe, and export the records to separate shapefiles by county
3. Merge the shapefiles of counties into a combined national street centerline file

The code of Function 2 was inherited from https://github.com/zxy1219/2000-Census-TIGER-LINE (X Zhang R Liu,2017) with some of my modifications:
1. Support converting street centerlines not in North American continent
2. Support reading streets with non-English characters
3. Use GeoPands and Shapely instead of ArcPy
