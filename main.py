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
from osgeo import gdal
import zipfile


abspath = os.path.abspath(sys.argv[0])
dname = os.path.dirname(abspath)
os.chdir(dname)

import TigerReportFile2Shapefile as t2s
import TigerReportFile2Shapefile_notgoodforAK as t2s_fast

ftp=FTP('ftp2.census.gov')
ftp.login()

ftp.cwd('geo/tiger/tiger2k')

statelist=ftp.nlst()
statelist=[x for x in statelist if len(x)==2]

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


