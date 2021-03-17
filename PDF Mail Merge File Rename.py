# Import Dependencies
import pandas as pd
import os
from datetime import datetime
import shutil


# Creating Necessary Values:
date_x = datetime.now().strftime("%m-%d-%y")


# Input Starting Directory and Ending Directory:
src = 'F:\\Mass Tort Cases\\Medicare spreadsheets\\Procedures\\1-Claims Request Query\\In Data Processing'
base_path = 'F:\\Mass Tort Cases\\Medicare spreadsheets\\Procedures\\1-Claims Request Query\\Processed\\Richard'
dest = os.path.join(base_path, "CPL Request - " + date_x)
copy_path = 'F:\\Mass Tort Cases\\Medicare spreadsheets\\Procedures\\1-Claims Request Query\\Processed\\Richard\\Copy'
os.chdir(src)


# Make Directory for Destination:
if os.path.isdir(dest):
    print ('Destination folder already exits')
else:
    os.mkdir(dest)
    print ("Created destination directory")


# Copy files to copy directory:
src_files = os.listdir(src)
for file_name in src_files:
    full_file_name = os.path.join(src, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, copy_path)
print("Copied filed to new directory")


# Read in Excel File to create filename list and delete extraneous files:
for file in os.listdir(src):
    if file.endswith(".xlsx"):
        f_name = os.path.abspath(file)
        df = pd.read_excel(f_name)
        os.remove(f_name)
    if file.endswith(".docx"):
        os.remove(file)

df['FileName'] = df['Last Name'] + ", " + df['First Name'] + " - Mcare - CPL Request - " + date_x + ".pdf"
file_list = df['FileName'].tolist()


# Rename the files in the destination folder:
i = 0
for file in os.listdir(src):
    if file.endswith('.pdf'):
        my_dest = str(file_list[i])
        my_source = min([os.path.join(src,d) for d in os.listdir(src)], key=os.path.getmtime)
        my_dest = dest + "\\" + my_dest
        os.rename(my_source, my_dest)
        i += 1