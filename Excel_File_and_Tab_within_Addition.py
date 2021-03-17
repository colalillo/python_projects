# Import Dependencies
import xlsxwriter
import xlrd

import pandas as pd
import os
import numpy as np


# Define directory and the files
dir = os.getcwd()
files = os.listdir(dir)

# Creating data frame to add to later
zz = pd.DataFrame()

# Iterate through files in directory to get the full name
for file in files:
    fullpath = dir + "\\" + file
    fpdub = fullpath

    # Open each file and create a list of the tab names
    xls = xlrd.open_workbook(fpdub, on_demand=True)
    n_list = xls.sheet_names().remove('Summary')

    # Add all of the tabs from all of the files together (and remove those without a lien id)
    df = pd.concat(pd.read_excel(fpdub, sheet_name=n_list), ignore_index=True)
    clean_df = df[df['LIEN_ID'].isna() == False]
    zz = zz.append(clean_df)


# Create a pivot to sum the lien amounts of the data
piv = zz.groupby(['FIRST_SNAME','LAST_NAME'])['NET_PAID_AMT'].sum().reset_index()   


# Export the data to a file with one sheet containing all of the merged data, and one sheet containing the summed lien amounts
writer = pd.ExcelWriter('Final_File.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name = 'Full Claims List', index = False)
piv.to_excel(writer, sheet_name = 'Pivot with Amounts', index = False)
writer.save()