# Python script containing AWS Lambda handler function to process the json files in source S3 bucket 
# and converts them to .csv in the destination S3 bucket by calling the file conversion script json_conversion script and reusable function

from __future__ import print_function

# importing modules such as boto3 to conenct to AWS
import csv
import sys
import os
import pandas as pd
import shutil
import glob
import json_conversion
import urllib
from datetime import datetime
import boto3
import botocore
import ctypes
from io import BytesIO

# use python logging module to log to CloudWatch
import logging
logging.getLogger().setLevel(logging.DEBUG)
#logging.debug('Start')

# must load all shared libraries in lib directory
for file in os.listdir('lib'):
    if os.path.isfile(os.path.join('lib', file)):
        ctypes.cdll.LoadLibrary(os.path.join('lib', file))

def handler(event,context):

        # Estabishing boto3 S3 connection and assigning the temp, source and dest bucket names
	s3 = boto3.resource('s3')
	source_bucket_name = 'json-to-csv-source'
	temp_bucket_name = 'json-temp-file-generator'
	destination_bucket = 'json-to-csv-destination'

	source_bucket = s3.Bucket(source_bucket_name)
        # Checking if the source S3 bucket exists
	if source_bucket in s3.buckets.all():
		# Fetching the input .json file which triggers this Lambda function execution
		key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'])
		key = key.encode('utf-8')
                # copy the json file from temp S3 bucket to source bucket
		copy_source = { 'Bucket': temp_bucket_name, 'Key': key }
		s3.meta.client.copy(copy_source, source_bucket_name, key)

		# Downloading the Input File to the '/temp/' ephemeral storage directory of Lambda
		try:
			s3.Bucket(source_bucket_name).download_file(key, '/tmp/' + key)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
			else:
				raise

		# calling function to convert json to csv
		output_csv_file = json_conversion.convert_json_to_csv('/tmp/' + key)

                # To verify if destination S3 bucket exists and if not, then to create it
		if not destination_bucket in s3.buckets.all():
			s3.create_bucket(
			Bucket=destination_bucket)

                # Writing the output_csv_file dataframe as .csv file in the destination S3 bucket 
                # using the buffer object in BytesIO()
		csv_buffer = BytesIO()
		output_csv_file.to_csv(csv_buffer)
		output_key = str.replace(key, '.json', '.csv')
		s3.Object(destination_bucket, output_key).put(Body=csv_buffer.getvalue())
	        print("json files converted to csv successfully")

	else:
		# To create the S3 Source bucket
                s3.create_bucket(
		Bucket=source_bucket_name)

	        temp_bucket = s3.Bucket(temp_bucket_name)
	        suffix = '.json'

                # To iterate across all the .json input files in the temp S3 bucket, one at a time,
                # and copy them to the source bucket
                # to convert them into .csv files and load them in the destination S3 bucket
	        for obj in temp_bucket.objects.filter():
		    key = '{1}'.format(temp_bucket, obj.key)
		    print(key)
		    if suffix in key:
                        copy_source = { 'Bucket': temp_bucket_name, 'Key': key }
			s3.meta.client.copy(copy_source, source_bucket_name, key)
                    FilesNotFound = False

                    # Downloading the Input json File to the '/temp/' directory of Lambda
                    try:
                        s3.Bucket(source_bucket_name).download_file(key, '/tmp/' + key)
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                                print("The object does not exist.")
                        else:
                                raise

		    # calling function to convert json to csv
		    output_csv_file = json_conversion.convert_json_to_csv('/tmp/' + key)
                    
                    # To verify if destination S3 bucket exists and if not, then to create it
		    if not destination_bucket in s3.buckets.all():
			s3.create_bucket(
			Bucket=destination_bucket)
                    
                    # Writing the output_csv_file dataframe as .csv file in the destination S3 bucket
                    # using the buffer object in BytesIO()
		    csv_buffer = BytesIO()
		    output_csv_file.to_csv(csv_buffer)
		    output_key = str.replace(key, '.json', '.csv')
		    s3.Object(destination_bucket, output_key).put(Body=csv_buffer.getvalue())

                if FilesNotFound:
                    print("ALERT", "No file in {0}/{1}".format(bucket, Input_Prefix))

	        print("json files converted to csv successfully")
