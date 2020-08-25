# Import Dependencies
import pandas as pd
import os
from datetime import datetime
from CaseNames import case_name_dict


# Setting Paths and Filenames
dir_date = datetime.now().strftime("%Y_%m_%d")
# dir_date = '2020_08_11'
dir_year = datetime.now().strftime("%Y")
in_filename = 'Full_Analysis.xlsx'
out_filename = 'Unlock_List.xlsx'
missing_info = 'HI Missing Info List.xlsx'
base_path = 'F:\\Mass Tort Cases\\TVM\\Claims Online\\Updates'
in_filepath = os.path.join(base_path, dir_year, dir_date, in_filename)
out_filepath = os.path.join(base_path, dir_year, dir_date, out_filename)
missing_out_path = os.path.join(base_path, dir_year, dir_date, missing_info)


# Checks for Paths and Filenames
print(f'Directory (Day): {dir_date}')
print(f'Directory (Year): {dir_year}')
print(f'File in path: {in_filepath}')
print(f'File out filepath: {out_filename}')
print(f'File for missing info filepath: {missing_out_path}')
print('Importing Full Analysis file...')


# Importing Full Analysis
df = pd.read_excel(in_filepath)
print('Full Analysis Imported')


# Creating Happy Path DataFrame
HP = df[(df['CMS_Label'].isin(['Add Lien', 'Happy Path']))]\
        [['COL Claim Number', 'COL Case Name']]\
        .drop_duplicates(subset=['COL Claim Number', 'COL Case Name'])
HP['Type'] = 'Happy Path'
print('Happy Path Dataframe created')


# Basic Human Intervention DataFrame
HI = df[(df['CMS_Label'].isin(['Human Intervention (fix this week)', 'Human Intervention (fix this week) (if time)', 'Look Into']))]\
        [['COL Claim Number', 'COL Case Name', 'Current Escrow', 'Percent Escrow Remaining_x', 'COL SA','SLAM SA']]\
        .drop_duplicates(subset=['COL Claim Number', 'COL Case Name'])\
        .dropna(subset=['Current Escrow','COL Case Name'])\
        .loc[df['Percent Escrow Remaining_x'] > .199]\
        [['COL Claim Number', 'COL Case Name']]
HI['Type'] = 'Human Intervention'
print('Normal Human Intervention Dataframe created')


# No COL Escrow DataFrame
HI_0E = df[(df['CMS_Label'].isin(['Human Intervention (fix this week)', 'Human Intervention (fix this week) (if time)', 'Look Into']))]\
        [['SLAM ThirdPartyId', 'SLAM CaseName', 'Current Escrow', 'Percent Escrow Remaining_x', 'COL SA', 'SLAM SA', 'Escrow Analysis']]\
        .loc[df['Percent Escrow Remaining_x'].isnull() == True]

HI_0E['SLAM SA'] = HI_0E['SLAM SA'].replace('[$,]', '', regex=True).astype(float)
HI_0E['Type'] = 'Human Intervention - Missing COL Escrow'
HI_0E['True Percent'] = HI_0E['Current Escrow'] / HI_0E['SLAM SA']

HI_0E = HI_0E.drop_duplicates(subset=['SLAM ThirdPartyId', 'SLAM CaseName'])\
        .loc[(HI_0E['True Percent'] > .199) & (HI_0E['Escrow Analysis'] != 'Not Eligible - not final in SLAM')]\
        [['SLAM ThirdPartyId', 'SLAM CaseName', 'Type']]\
        .rename(columns = {'SLAM ThirdPartyId': 'COL Claim Number', 'SLAM CaseName': 'COL Case Name'})
HI_0E['COL Case Name'] = HI_0E['COL Case Name'].replace(case_name_dict, regex = True)
print('Human Intervention with missing COL Escrow Dataframe created')


# Missing all COL #'s but with escrow Dataframe 
HI_DF = df[(df['CMS_Label'].isin(['Human Intervention (fix this week)', 'Human Intervention (fix this week) (if time)', 'Look Into']))]\
        .loc[df['Percent Escrow Remaining_x'].isnull() == True]\
        .loc[df['SLAM ThirdPartyId'].isnull() == True]
HI_DF['Type'] = 'WTF - More Analysis Needed'

HI_DF.to_excel(missing_out_path, index = False)
print('Missing information Dataframe created')


# Create final unlock DataFrame
final_df = pd.concat([HP, HI_0E, HI]).sort_values(['COL Case Name'])
final_df.to_excel(out_filepath, index = False)
print('Unlock list exported to file')