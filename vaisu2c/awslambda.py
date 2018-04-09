'''
Created on Jan 25, 2018

@author: zack.ramjan
'''

import boto3
import botocore
import urllib
import os
import time
import sys

     

#retrieves the instance cloud-init script that will need to be modifiied and passed to the instance creation call
def createCloudInit(path):
    f = urllib.urlopen("https://s3.us-east-2.amazonaws.com/su2csoftware/bootstrap/bootstrap.sh")
    initString = f.read()
    
    # add a line to the scriptfor the actual analysis
    initString += "python /tools/AwsS3.py " + path + "\n"
    
    #and then a line that shuts down the instance
    initString += "shutdown -h now \n"
    #print(initString)
    return initString


#this handler is called when a new file is detected on the s3 bucket     
def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        
        #make sure only fire up an instance  on incoming new data, not on already analyzed data, otherwise we loop forever. 
        if "analysis" in key.lower(): return 
        
        #create cloud init script for the instance
        initScript = createCloudInit(bucket + "/" + key)
        
        #create ec2 instance, there are many args that can be passed to instance creation, but instead we reference an existing ec2 launch template
        ec2 = boto3.resource('ec2')
        instance = ec2.create_instances(
            ImageId='ami-f63b1193',
            MinCount=1,
            MaxCount=1,
            UserData=initScript,
            LaunchTemplate= {'LaunchTemplateName':"su2c_worker", 'Version':"5"},
            InstanceType='t2.micro')
        print(instance[0].id)
