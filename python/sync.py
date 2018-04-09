#!/usr/bin/env python3
'''
Created on Mar 30, 2018

@author: zack.ramjan
'''

import boto3 #AWS package
import botocore #AWS package
import urllib
from os import path, listdir, walk
import time
import socket
import sys
import re
import glob
import csv
from shutil import copy2


class SampleData:
   """holds data and files for a sample"""
   sampleID = ""
   study = ""
   site = ""
   platform = ""
   files = []

   def print(self):
      print(self.sampleID,self.study,self.site,self.platform)
      for f in self.files:
         print("\t"+f)
      print("")

   def sync(self,destinationRoot):
      if not path.isdir(destinationRoot): sys.exit();      
      for f in self.files:
         #copy2(f,destinationRoot)
         print("\t\tcopy2(" + f,destinationRoot +")")
         


def getEpicSamplesFromDir(rootPath):
   """given a data root (rootPath) find all run dirs and samplesheets and process them."""
   epicSamples=[]
   current, dirs, files = next(walk(rootPath))
   for dir in filter(lambda x: re.match(".*20.*",x), dirs): 
      current, subdirs, files = next(walk(path.join(rootPath,dir))) 
      for subdir in filter(lambda x: re.match("[0-9]+",x), subdirs):
         dataDir =  path.join(rootPath,dir,subdir)
         samplesSheets = glob.glob(dataDir + "/*.csv")
         for ss in samplesSheets:
            epicSamples.extend(readEpicSampleSheet(ss))
            break #WE ONLY TAKE THE FIRST SAMPLE SHEET FOUND IN A RUN DIR!
   return epicSamples

def readEpicSampleSheet(sampleSheetPath):
   """given a sampleSheet path, parse and return a list of SampleData"""
   inData=False
   sampleSheetRows=[]
   sampleDataRows=[]
   with open(sampleSheetPath) as sampleSheet:
      for row in sampleSheet:
         if inData: sampleSheetRows.append(row) 
         if re.match("\[Data\].+", row): inData=True
   reader=csv.DictReader(sampleSheetRows)
   if len(sampleSheetRows) < 1 or 'Sample_ID' not in sampleSheetRows[0] or 'SentrixPosition_A' not in sampleSheetRows[0] or  'SentrixBarcode_A' not in sampleSheetRows[0]: return []
   for row in reader:
      entry=SampleData()
      entry.sampleID = row['Sample_ID']
      entry.study = "UKNOWN-Study"
      entry.site = "UKNOWN-site"
      entry.platform = "iscan"
      files = glob.glob(path.dirname(sampleSheetPath) + "/" + row['SentrixBarcode_A'] + "_" + row['SentrixPosition_A'] + "_*")
      entry.files = files
      sampleDataRows.append(entry)
   return sampleDataRows
   
def readDynamo():
   """reads the dynamo DB. MUST HAVE CREDENTIALS SET. use ~/.aws/credentials and .aws/config"""
   dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
   table=dynamodb.Table('Su2cBsiData')
   response=table.scan()
   for item in response['Items']:
      print(item['bsiID'],item['collectionCenter'],item['anatomicSite'])
 


#retrieve the instance user-defined meta-data.
#not used anymore since we use cloud-init to run a startup script 

#print the AWS temp auth keys assigned to this instance. Not Actually needed
#since boto3 handles all this behind the scenes
def awstempkeys():

    session = boto3.Session()
    credentials = session.get_credentials()

    # Credentials are refreshable, so accessing your access key / secret key
    # separately can lead to a race condition. Use this to get an actual matched
    # set.
    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    print(credentials, "a\n",access_key, '\n\n', secret_key)

#samples = getEpicSamplesFromDir("/primary/instruments/iscan")
#for s in samples:
#   s.sync("/mnt/su2cdataraw")
#   s.print()

readDynamo()
