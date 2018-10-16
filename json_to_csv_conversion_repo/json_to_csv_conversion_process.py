# To process the latest JSON file uploded in a source location, by converting it into .csv format and then loading it into a target directory 
# locally  (File locations to be configurable at script)

# Main script which configures temp, source and dest directories and calls the function convert_json_to_csv from the python script
# json_conversion.py by importing it as a custom module

# Importing required python modules
import csv
import sys
import os
import pandas as pd
import shutil
import glob
import json_conversion

# tmp_dir, source and dest paths executed inside an AWS EC2 instance
source = "/home/ec2-user/src/"
tmp_dir = "/home/ec2-user/tmp/"
dest = "/home/ec2-user/dest/"

# To check if source dir exists, and to fetch the latest file from the tmp dir (location where latest JSON files are generated)
if os.path.isdir(source):
    list_of_files = glob.glob(tmp_dir + "*.json")
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.endswith(".json"):
        shutil.copy(latest_file,source)
    file_path = str.replace(latest_file, 'tmp', 'src')
    
    # calling function to convert json to csv
    output_csv_file = json_conversion.convert_json_to_csv(file_path)
    # to create destination dir
    if not os.path.isdir(dest):
        os.makedirs(dest)

    output_file_name = str.replace(str.replace(file_path, 'src', 'dest'), 'json', 'csv')

    # To write output .csv files in destination
    output_csv_file.to_csv(output_file_name)

else:
    # To create source directory
    os.makedirs(source)
    for files in os.listdir(tmp_dir):
        file_name = os.path.join(tmp_dir, files)
        if file_name.endswith(".json"):
            # to copy files from tmp dir to source dir
            shutil.copy(file_name,source)
        file_path = str.replace(file_name, 'tmp', 'src')
    
        # calling function to convert json to csv
        output_csv_file = json_conversion.convert_json_to_csv(file_path)
        # to create destination dir
        if not os.path.isdir(dest):
            os.makedirs(dest)

        output_file_name = str.replace(str.replace(file_path, 'src', 'dest'), 'json', 'csv')

        # To write output .csv files in destination
        output_csv_file.to_csv(output_file_name)
