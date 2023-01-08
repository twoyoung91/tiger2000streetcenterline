import re
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, shape

#Original GitHub url: https://github.com/zxy1219/2000-Census-TIGER-LINE
__originalauthor__ = 'liurl1221@gmail.com'
__originalauthor__ = 'zxy1219@gmail.com'
__editedby__ = 'me@yangyang.city'

# split the point
def splitPoint(point):
    value = []
    points=re.split('(?=[+-])',point)
    value.append(float(points[1])/1000000)
    value.append(float(points[2])/1000000)
    return value

# read data from RT2 file and store in dictionary. RT2 file stored the turning point of the lines in RT1
# key: numbers start with 7;
# value: geo location
def readRT2toDic(inputfolder,inputname):
    f = open(inputfolder+"/"+inputname+'.RT2')
    RT2_dic = {}
    for line in f:
        line = line.strip()
        columns = line.split()
        if len(columns)==3:
            coords=columns[2]
            coords=re.split('(?=[+-])',coords)
            columns[2]=coords[0]
            coords=[x for x in coords if x[:2]!="+0"]
            for num1,num2 in zip(coords[1::2],coords[2::2]):
                columns.append(num1+num2)
        tps = [];
        for index,col in enumerate(columns):
            if index == 1:
                key = col
            elif index > 2:
                value = splitPoint(col) #split the turning point
                tps.append(value)
        if key in RT2_dic.keys():
            cval=RT2_dic[key]
            cval=cval+tps
            RT2_dic[key] = cval
        else:
            RT2_dic[key] = tps
    return RT2_dic

# read data from RT1 file and store in an array. RT1 file stores the types, starting coordination, and ending coordination of lines
def readRT1toArray(inputfolder,inputname):
    # load RT2 to dictionary
    RT2_dic = readRT2toDic(inputfolder,inputname)
    
    f = open(inputfolder+"/"+inputname+'.RT1',encoding="windows-1252")
    feature_info = pd.DataFrame(columns=["id","x","y","type"])
    for line in f:
        line = line.strip()
        linetype = line[55:58]
        line=line.replace("-"," -")
        line=line.replace("+"," +")
        columns = line.split()
        startPoint = columns[-4]+columns[-3]
        endPoint = columns[-2]+columns[-1]
        ref = columns[1]    # number starts with 7

        #if road name starts with 'A'
        if(linetype[0]== 'A'):
            temp = [];

            # add start point
            a = splitPoint(startPoint)
            temp.append(a)

            # add turning points if turning points exist
            if(ref in RT2_dic):
                tps = RT2_dic[ref]
                temp += tps

            # add end point
            b = splitPoint(endPoint)
            temp.append(b)
            
            
            # add ref and road type to the list
            
            roaddf=pd.DataFrame(temp,columns=["x","y"])
            roaddf['id']=ref
            roaddf['type']=linetype
            
            feature_info=feature_info.append(roaddf)
    return feature_info

#Original Solution via arcpy
# if __name__ == "__main__":

#     # A list of features and coordinate pairs
#     # A list that will hold each of the Polyline objects
#     features = readRT1toArray()
#     for feature in features:
#         # Create a Polyline object based on the array of points
#         # Append to the list of Polyline objects
#         features.append(
#             arcpy.Polyline(
#                 arcpy.Array([arcpy.Point(*coords) for coords in feature])))

#     # Persist a copy of the Polyline objects using CopyFeatures
#     arcpy.CopyFeatures_management(features, "*****/Tiger/rd_2ktiger/TX/polylines2.shp")

#New Solution with Geopandas and shapely
def convertascii(inputfolder,inputname,outputfolder):
    # create vertices from the RT1 and RT2 files
    points = readRT1toArray(inputfolder,inputname)
    if points.shape[0]==0: return
    
    #convert points to geopandas point object
    geometry= [Point(xy) for xy in zip(points.x, points.y)]
    geo_df = gpd.GeoDataFrame(points, geometry=geometry)
    
    #generate polyline geodataframe
    geo_df2 = geo_df.groupby(['id','type'])['geometry'].apply(lambda x: LineString(x.tolist()))
    geo_df2 = gpd.GeoDataFrame(geo_df2, geometry='geometry')

    #export shapefile
    geo_df2.to_file(filename=outputfolder+"/"+inputname+".shp",driver='ESRI Shapefile',crs="epsg:4269")

if __name__ == "__main__":
    ...
