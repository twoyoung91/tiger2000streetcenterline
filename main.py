# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 23:08:19 2023

@author: TwoYoung(me@yangyang.city)
"""
import os
import sys
import pandas as pd
import geopandas as gpd
from ftplib import FTP
import zipfile

abspath = os.path.abspath(sys.argv[0])
dname = os.path.dirname(abspath)
os.chdir(dname)

import TigerReportFile2Shapefile as t2s
import TigerReportFile2Shapefile_fast as t2s_fast

ftp=FTP('ftp2.census.gov')
ftp.login()

ftp.cwd('geo/tiger/tiger2k')

statelist=ftp.nlst()
statelist=[x for x in statelist if len(x)==2]

#download Tiger2k RT files and convert to shapefiles
for state in statelist[28:]:
    if not os.path.exists(state):
        os.makedirs(state)
    ftp.cwd(state)
    filelist=ftp.nlst()
    filelist=[x for x in filelist if x[-3:]=="zip"]
    for file in filelist:
        filename=state+"/"+file
        if not os.path.exists(filename):
            print ("processing "+state+" "+file)
            #download file
            try:
                ftp.retrbinary('RETR ' + file,open(filename, 'wb').write)
            except:
                print("connection lost, try reconnecting!")
                ftp=FTP('ftp2.census.gov')
                ftp.login()
                print("reconnected!")
                ftp.cwd('geo/tiger/tiger2k')
                ftp.cwd(state)
                ftp.retrbinary('RETR ' + file,open(filename, 'wb').write)
            #extract zip file
            tigerpack=zipfile.ZipFile(filename)
            dirname=filename[:-4]
            tigerpack.extractall(path=dirname)
            #convert ASCII files to shapefile
            try:
                t2s_fast.convertascii(inputfolder=os.getcwd()+"/"+dirname,inputname=file[:-4],outputfolder=os.getcwd()+"/"+state)
            except:
                print("fast method failed, try backup method")
                t2s.convertascii(inputfolder=os.getcwd()+"/"+dirname,inputname=file[:-4],outputfolder=os.getcwd()+"/"+state)         

    ftp.cwd('..')

#Merge shapefiles for each state
if not os.path.exists("merged shapefiles"):
    os.makedirs("merged shapefiles")
for state in statelist:
    if not os.path.exists("merged shapefiles/"+state+".shp"):
        print ("merging shapefiles for "+state)
        countylist=os.listdir(state)
        countylist=[x for x in countylist if x[-3:]=="shp"]
        stateshape=gpd.GeoDataFrame(columns=['id', 'x', 'y','type','geometry'], geometry='geometry',crs="epsg:4269")
        for shapefile in countylist:
            countyshape=gpd.read_file(state+"/"+shapefile)
            stateshape=gpd.pd.concat([stateshape,countyshape])
        if stateshape.shape[0]!=0:
            stateshape.to_file("merged shapefiles/"+state+".shp")
        else:
            print (state+" does not have any street records.")
    else:
        print (state+" shapefile already exists, and it is skipped.")
        

#Merge state shapefiles into a national one
nationshape=gpd.GeoDataFrame(columns=['id', 'x', 'y','type','geometry'], geometry='geometry',crs="epsg:4269")
for state in statelist:
    if not os.path.exists("merged shapefiles/"+state+".shp"):
        print (state+" does not have a street shapefile, and it is skipped.")
    else:
        print ("merging shapefiles from "+state)
        stateshape=gpd.read_file("merged shapefiles/"+state+".shp")
        nationshape=gpd.pd.concat([nationshape,stateshape])
nationshape.to_file("merged shapefiles/USstreets2000.shp")
        
