# awsfun
Exploring AWS in python


## To Deploy:
unpack the repo with dir structure intact to public s3 bucket  su2csoftware
make sure not to make the private dir public.

# Overview and Architecture
### prereqs
Log into the main EC2 "master" account:  639677452477
You need to have be able to switch into the su2c admin role. This can be done be reading the "AWS user roles.pdf"
switch roles to account=197833163604 role=su2cadmin . If you have the correct permissions you will now be operating as an admin in the su2c account.

roles with associated policieshave already been created. One is the su2cadmin role with administrative rights that applies to AWS admins wanting to view the console. THere are also roles for EC2, Lambda and S3. A Role is analogous to an old-fashioned "service account" except inherently safer and more stable due to not being a true account tied to a real (or fake) user. Every role has a set of "policies" assoctiated with it. This are basically what that roles is allowed/not-allowed to do. These policies can get very complex, there are hundreds of possible privileges that can be toggled on/off. For simplicities sake, I am using "job function" policies which are common subsets of privileges based upon typical needs. For example "admin" and "power-user". We probably want to fine tune this down the line. For this prototype, the AWS service-derived roles (EC2,Lambda,S3, ie privileges that services can execute as) are using policies that reference the default "power-user" pre-set privileges.  

### EC2
EC2 is pretty straight forward, you run instances (aka VM's there). The special areas of concern are with regards to policy/role and cloud-init. Given that we want lambda to spin up an instance based upon data arriving in S3, we need a means to pass the location of the data into the instance. This is accomplished with the instance "user-data" which is basically a bash script that gets executed once the instance is loaded. the template for this bash script is bootstrap/bootstrap.sh. Once the processing is done, we shutdown down VM. 

There are many parameters that can be set for an instance, such as the source image (linux version), shutdown behavior, disk layout, network settings etc. these could have been set directly in the lambda python function, but rather I have created a "launch template" called "su2cw_worker" within the AWS EC2 console that has these defaults set. we may require different launch templates depending on on the work to be performed. There is a template setting to give the instance a "role" called ec2_instnance_power (which references the default power-user permissions) so that it can see privileged data in the S3 bucket.  

### S3

S3 is online storage and we have two S3 buckets: one for software and one for data. the software one is public since we want the lambda function to be able set up the bootstrap. The instance will also pull down its python code to execute AwsS3.py at runtime from the software bucket.

The other bucket is for data and is private. This bucket has a trigger set such that any new files trigger the lambda event.


### Lambda 
The lambda function is responsible for spawning a new EC2 instance when a new file apears in the S3 data bucket. We create a string with bootstrap.sh code, add a line for the path to the new file, then create the instance using the EC2 API. We want to only spawn a processing instance on new data, not newly added output originating from the VM, therefore we make sure the newly-added filename does not contain the substring "analysis". Like the other services, lambda requires a IAM role with associated polcies such that it can perform the neccesary work. As usual, we give it the default "power-user" set of privileges. 

The lambda function code gets cut and pasted via the web based AWS console. For testing purposes, you can simulate the "S3 file added" event by pasting in the lambda_test_event.json in the AWS console lambda designer gui. 


# issues
currently experiencing some weirdness with policy permissions, lambda complaining that it isnt "allowed to create the instance". so had to set lambda role to "admin" level privs, also set ec2 to same level since currently troubleshooting. we should change this to sane values. 
BUT IT IS WORKING!
