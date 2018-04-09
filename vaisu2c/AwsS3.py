#!/usr/bin/env python
'''
Created on Jan 22, 2018

@author: zack.ramjan
'''

import boto3
import botocore
import urllib
import os
import time
import socket
import sys

#given a bucket and key, download the file and save locally as 'localfile'
def downloadFile(bucket, key,localfile):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket).download_file(key, localfile)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

#upload the local file 'localfile', it will be stored as 'key' on S3 in the given bucket
def uploadFile(bucket, key, localfile):
    # Upload a new file
    s3 = boto3.resource('s3')
    data = open(localfile, 'rb')
    s3.Bucket(bucket).put_object(Key=key, Body=data)

#retrieve the instance user-defined meta-data.
#not used anymore since we use cloud-init to run a startup script 
def getUserInstanceMeta():
    #get payload target
    f = urllib.urlopen("http://169.254.169.254/latest/user-data")
    metastring = f.read()
    print "user-data from instance meta-data:", metastring
    return metastring

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

#a trivial analysis function that represents the "work". later on this would be a long running genomics analysis
def doAnalysis(inputFile):
    f=open(inputFile, "a+")
    f.write("These lines were added at " + str(int(time.time())) + " on machine " + socket.gethostname() + "\n")


#get the program arguement and seperate into its bucket and key 
#(bucket,dl,path) = getUserInstanceMeta().partition('/');
(bucket,dl,path) = sys.argv[1].partition('/');
print bucket, dl, path
if path:
    localFile = os.path.basename(path)
    downloadFile(bucket,path, localFile)
    doAnalysis(localFile)
    uploadFile(bucket,path + ".analyzed." + str(int(time.time())), localFile)
else:
    print "no s3 object path found, looping over buckets and files"
    #otherwise someting is not right, lets just loop over the files and do something harmlesss and dumb.
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        for key in bucket.objects.all():
            if "directory" not in key.Object().content_type:
                print(key.bucket_name,key.key,key.Object().content_type)
                #download the existing file
                localFile = os.path.basename(key.key)
                #downloadFile(key.bucket_name,key.key, localFile)
                #Analysis(localFile)
                