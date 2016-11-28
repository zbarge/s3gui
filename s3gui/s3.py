# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import boto3
from subprocess import call

class S3Client():
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.client = self.s3.meta.client
        self._key_registry = {}
        
    def nlst(self, bucket):
        contents = []
        paginator = self.client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Delimiter='/'):
            for prefix in result.get('CommonPrefixes', []):
                contents.append(prefix.get('Prefix'))
        return contents
                
    def get_bucket_names(self):
        return [bucket.name for bucket in self.s3.buckets.all()]
        
    def get_prefix_dirname(self, prefix):
        if "." in prefix:
            parts = prefix.split("/")
            parts.pop()
            prefix = "/".join(parts) + "/"
            
        return prefix
        
    def move_file(self, from_bucket, from_key, to_bucket, to_key):
        """
        Moves a file from one bucket to another.
        Inefficient for moving many files
        as the to_bucket is requested each time.
        """
        copy_source = {'Bucket': from_bucket,
                       'Key': from_key}
        bucket = self.s3.Bucket(to_bucket)
        bucket.copy(copy_source, to_key)
        return True
        
    def sync_directory(self, dirname, bucket_name, key_name=None, exclude=None):
        base_path = bucket_name
        bp = (key_name if key_name is not None else "")
        if bp.startswith("/"):
            bp = bp[1:]
        if bp.endswith("/"):
            bp = bp[:-1]
            
        if base_path.endswith("/"):
            base_path = base_path[:-1]

        base_path += "/" + bp
        
        if base_path.endswith("/"):
            base_path = base_path[:-1]
        
        cmd_list = ["cmd",
                    "/c",
                    "aws",
                    "s3",
                    "sync",
                    dirname,
                    "s3://{}".format(base_path)]
        if exclude:
            cmd_list.extend(['--exclude', exclude])
        print("Executing command: {}".format(cmd_list))          
        
        return call(cmd_list)
        
    def combine_buckets(self, to_bucket, excludes):
        """
        Merges all buckets not in the list of
        excludes into the to_bucket.
        Empty buckets/folders are deleted.
        to_bucket must exist...
        """
        to_bucket = self.s3.Bucket(to_bucket)
        
        #Iterate through all buckets
        for bucket in self.s3.buckets.all():
            
            if bucket.name not in excludes:
                bfolders = []
                #Iterate through all objects
                #in bucket
                for obj in bucket.objects.all():
                    
                    try:
                        #Move & delete files
                        if "." in obj.key:
                            to_bucket.copy({'Bucket':bucket.name, 'Key':obj.key},
                                           "/".join([bucket.name, obj.key]))
                            obj.delete()
                        else:
                            #Save folders to delete last
                            bfolders.append(obj)
                            
                    except Exception as e:
                        print("Failed on bucket {} and obj {} - {}".format(
                              bucket.name, obj, e))
                        
                try:
                    #remove the (assumed)
                    #empty folders
                    for folder in bfolders:
                        folder.delete()
                    #remove the (assumed)
                    #empty bucket
                    bucket.delete()
                    
                except Exception as e:
                    print("Failed to delete bucket {}, error: {}".format(
                          bucket.name, e))    
        

if __name__ == '__main__':
    ac = S3Client()

    
    
    
    #The buckets to keep
    excludes = ['zeke1',
                'abackup1',
                'aecimages',
                'iswap', 
                'autoecrafters', 
                'trend_data']
    #ac.client.create_bucket(Bucket="trend_data")
    
    #The new bucket
    to_bucket = "trend_data"
    
    
    dirname = "C:/log"
    bucket_name = "zeke1"
    res = ac.sync_directory(dirname, bucket_name, key_name=None, exclude=None)
    print(res)

            
            
            
            
    
    
    
    
    

