# Import dependencies:
import pandas as pd
import os
import numpy as np

from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from datetime import date
from datetime import datetime

import xlsxwriter
import xlrd

import CaseNames


# ----------------------------------------


# Create time object in correct format:
datex = datetime.now().strftime("%Y-%m-%d")
datey = datetime.now().strftime("%m/%d/%Y")

init_int_cases = [5263, 5070, 5223, 5280, 5150, 5239]
not_init_int_cases = [5022, 4073, 4074, 5224]
init_cases = [str(i) for i in init_int_cases]
not_init_cases = [str(i) for i in not_init_int_cases]

print(datex)
print(datey)
print(init_int_cases)
print(init_cases)
print(not_init_int_cases)
print(not_init_cases)


# ----------------------------------------


# create engine, make connection to reporting DB
engine = create_engine(CaseNames.engine_var)
metadata = MetaData(bind=engine)

# create dataframe from table pulled from sql
df = pd.read_sql(
"""
Select	
	Sub.[Ref SSN], 
	Sub.[Medicare Product Id], 
	Sub.ClientId, 
	Sub.PersonId,
	Sub.[Last Name], 
	Sub.[First Name],
	Sub.[Date of Birth],
	Sub.SSN, 
	Sub.Gender, 
	Sub.CaseName, 
	Sub.CaseId,
	Sub.Stage, 
	Sub.LienProductStatus, 
	Sub.Onbenefits,
	Sub.ClientDrugIngested,
	Sub.PrevSSN,
	Sub.ThirdPartyId, 
	Sub.CaseUserDisplayName,
	case
		when JB.[Universe Has Agreement to Participate from CMS?] like 'No%' then 'No'
		when JB.[Universe Has Agreement to Participate from CMS?] like 'Yes%' then 'Yes'
		when JB.[Universe Has Agreement to Participate from CMS?] like 'N/A%' or JB.[Universe Has Agreement to Participate from CMS?] like 'NEVER%' then 'Ignore'
		else 'Missing Info'
		end as 'Has ATP? Yes or No',
	Sub.[SSN & DOB Check],
	Sub.[Gender Check]
			From(
				Select
					ClientSSN as 'Ref SSN', 
					Id as 'Medicare Product Id', 
					ClientId, 
					PersonId,
					ClientLastName as 'Last Name', 
					ClientFirstName as 'First Name',
					convert(varchar, ClientDOB, 101) as 'Date of Birth',
					ClientSSN as 'SSN', 
					REPLACE(REPLACE(REPLACE(REPLACE(ClientGender, 'Female', '2'), 'Male', '1'), 'F', '2'), 'M', '1') as 'Gender', 
					CaseName, 
					CaseId,
					Stage, 
					LienProductStatus, 
					Onbenefits,
					REPLACE(REPLACE(ClientDrugInjested, CHAR(13), ''), CHAR(10), ' ') as 'ClientDrugIngested',
					PrevSSN,
					ThirdPartyId, 
					CaseUserDisplayName,
						CASE
							WHEN Stage like 'To Send - EV' and (ClientSSN like '%CMS%' or ClientSSN like '%NoSSN%' or ClientSSN like '%No SSN%' or ClientSSN like '%Reverify%'or ClientSSN like '' or ClientSSN is NULL or len(ClientSSN) <> 11 or ClientSSN like '%[a-z]%' or ClientSSN like '111-11-1111' or ClientSSN like '999-99-9999') AND (ClientDOB > '2010-01-01' or ClientDOB is NULL) then 'SSN and DOB Issue - Product should be @ Awaiting Information'
							WHEN Stage like 'Awaiting Information' and (ClientSSN like '%CMS%' or ClientSSN like '%NoSSN%' or ClientSSN like '%No SSN%' or ClientSSN like '%Reverify%' or ClientSSN like '' or ClientSSN is NULL or len(ClientSSN) <> 11 or ClientSSN like '%[a-z]%' or ClientSSN like '111-11-1111' or ClientSSN like '999-99-9999') AND (ClientDOB > '2010-01-01' or ClientDOB is NULL) then 'Correct Stage - Bad SSN & DOB'
							WHEN Stage like 'To Send - EV' and (ClientSSN like '%CMS%' or ClientSSN like '%NoSSN%' or ClientSSN like '%No SSN%' or ClientSSN like '%Reverify%' or ClientSSN like '' or ClientSSN is NULL or len(ClientSSN) <> 11 or ClientSSN like '%[a-z]%' or ClientSSN like '111-11-1111' or ClientSSN like '999-99-9999') then 'Invalid SSN - Product should be @ Awaiting Information'
							WHEN Stage like 'Awaiting Information' and (ClientSSN like '%CMS%' or ClientSSN like '%NoSSN%' or ClientSSN like '%No SSN%' or ClientSSN like '%Reverify%' or ClientSSN like '' or ClientSSN is NULL or len(ClientSSN) <> 11 or ClientSSN like '%[a-z]%' or ClientSSN like '111-11-1111' or ClientSSN like '999-99-9999') then 'Correct Stage - Bad SSN'
							WHEN Stage like 'To Send - EV' and (ClientDOB > '2010-01-01' or ClientDOB is NULL) then 'Invalid DOB - Product should be @ Awaiting Information'
							WHEN Stage like 'Awaiting Information' and (ClientDOB > '2010-01-01' or ClientDOB is NULL) then 'Correct Stage - Bad DOB'
							WHEN Stage like 'To Send - EV' then 'Correct Stage - Valid SSN and DOB'
							ELSE 'Valid SSN & DOB - Product should be at To Send - EV'
							END AS 'SSN & DOB Check',
						CASE
							WHEN ClientGender not like '1' or ClientGender not like '2' then 'Good'
							ELSE 'Issue'
							END AS 'Gender Check'
				FROM FullProductViews 
				WHERE LienType = 'Medicare - Global' 
					AND IsMt = 1
					AND (Stage like 'To Send - EV' or Stage like 'Awaiting Information')
 					AND LienProductStatus not like 'Hold'
					AND CaseName NOT LIKE '%Hold%' AND CaseName NOT LIKE '%Inactive%' and CaseName NOT LIKE '%Closed%' and CaseName NOT LIKE '%TVM%' AND CaseName NOT LIKE '%GRG%' AND CaseName NOT LIKE '%Duplicate%'
				) as Sub
					Left Join JB_MedicareReportReference as JB on Sub.CaseID = JB.[Case Id]
		Order By ClientDrugIngested, CaseId, ClientId
""",
con = engine
)


# ----------------------------------------


## Assigning Name to sql pull dataframe:
df.name = "- All Medicare Products -"

## Identifies repeating values in SSN column:
dupes = df.duplicated(['SSN'], keep=False)

## Creates Duplicate Check Column based on 'dupes' above:
df['Duplicate Check'] = np.select([dupes],['Duplicate SSN'], default='Good')

## Replaces values for those with Reverify, CMS Dropped, or No SSN:
df.loc[df.SSN == 'Reverify', ['Duplicate Check']] = 'OK - Other SSN Issue'
df.loc[df.SSN == 'CMSDropped', ['Duplicate Check']] = 'Ok - Other SSN Issue'
df.loc[df.SSN.isnull(), ['Duplicate Check']] = 'Ok - Other SSN Issue'
df.loc[df.SSN == '', ['Duplicate Check']] = 'Ok - Other SSN Issue'
df.loc[df.SSN == 'NULL', ['Duplicate Check']] = 'Ok - Other SSN Issue'
df.loc[df.SSN == 'No SSN', ['Duplicate Check']] = 'Ok - Other SSN Issue'
df.loc[df.SSN == '111-11-1111', ['Duplicate Check']] = 'Ok - Other SSN Issue'

## Applying Submission Column Logic Function
df['Submission'] = df.apply(func, axis = 1)


# ----------------------------------------


## Isolate work that Has ATP (or missing info) OR in Initial Cases
work = df[(df['Has ATP? Yes or No'].isin(['Yes', 'Missing Info'])) | (df['CaseId'].isin(init_cases))]
work.name = "'Isolation for To Submit Results'"

## Define Good to Go Product DF
good = work[(work['SSN & DOB Check'] == 'Correct Stage - Valid SSN and DOB') &
          (work['Gender Check'] == 'Good')]
good.name = "- To Submit -"

## Define Good to Go Product DF
initquest = df[(df['Has ATP? Yes or No'] != 'Yes') &
          (df['ClientDrugIngested'] != 'Pinnacle Hip Implant')  &
          (df['SSN & DOB Check'] == 'Correct Stage - Valid SSN and DOB') &
          (df['CaseId'].isin(init_cases) == False) &
          (df['CaseId'].isin(not_init_cases) == False)]
initquest.name = "- Possible Initial Cases -"

## Define Just Missing Gender DF
genbad = work[(work['SSN & DOB Check'] == 'Correct Stage - Valid SSN and DOB') &
          (work['Gender Check'] == 'Issue')]
genbad.name = "- Gender Issues -"

## Define Just Missing Gender DF
datebad = work[(work['SSN & DOB Check'] == 'Correct Stage - Bad DOB') &
          (work['Gender Check'] == 'Good')]
datebad.name = "- Date Issues -"

## Define Possible Stage Push DF
newstage = work[(work['SSN & DOB Check'] == 'Valid SSN & DOB - Product should be at To Send - EV') &
          (work['Gender Check'] == 'Good')]
newstage.name = "- Edit Stage to Push -"

## Point Out Duplicate Products for Claimant
dupeSSN = work[(work['SSN & DOB Check'] == 'Correct Stage - Valid SSN and DOB') &
          (work['Gender Check'] == 'Good') &
          (work['Duplicate Check'] == 'Duplicate SSN')]
dupeSSN.name = "- Duplicate Products -"

## Define Missing ClientDrugIngested DF
noCDI = df[df['ClientDrugIngested'].isna()]
noCDI.name = "- Fix ClientDrugIngested -"

## Define Bad work
bad = df.merge(good, how= 'left', on = 'Medicare Product Id', indicator = True).query('_merge == "left_only"').drop('_merge', 1)
bad_clean = bad.iloc[:,0:22]
## Rename Headers# print(initquest.index)
st = list(bad_clean.columns)
xp = ([s.replace('_x', '') for s in st])
bad_clean.columns = xp
bad_clean.name = "- Not Going or Issues -"


# ----------------------------------------


# List of ClientDrugIngested Adjusted Values that are Reverification Submissions
rever_lst = ['Pinnacle', 'TRT', 'Fluoroquinolone', 'Hog Farm', 'Stryker', 'TVM', 'Infuse', 'Invokana', 'Cymbalta', 'IVC', 'Mass Med-Mal', 'Abilify', 'Faulty Pacemaker Implant']

# Actual submission results test to see if on rever_lst:
rever_df = good[(good['CaseId'].isin(init_cases) == False)]
check_lst = list(rever_df.Submission.unique())

# Theoretically possible submission results test to see if on rever_lst:
rever_df_test = df[(df['CaseId'].isin(init_cases) == False)]
check_lst_test = list(rever_df_test.Submission.unique())

# Function to test if list is in another list, and if not, print what's missing:
def sub_adj(x,y):
    print(x)
    for i in x:
        if i in y:
            pass
        else:
            print(f'{i} needs to be adjusted either in the function(func) or in the rever_lst')
    print("")

# Test the actual submission results against the rever_lst:
print("All good to go reverification submission values and which ones need to be added:")
sub_adj(check_lst, rever_lst)

# Test the theoretical submission results against the rever_lst:
print("All ClientDrugIngested Values and which ones need to be added:")
sub_adj(check_lst_test, rever_lst)


# ----------------------------------------


## Create a list of the submissions and deficiency dataframes
df_tab_lst = [initquest, genbad, datebad, newstage, dupeSSN, noCDI]

## Create a space function to define spacing between the deficiency pivots
def space(i):
    return "\n" * i

## Create 'To Submit' Pivot (using submission column instead of case column)
good_piv = good.groupby(['Submission','CaseUserDisplayName'])['Medicare Product Id'].count().reset_index()
good_sort = good_piv.sort_values(['Submission']).set_index('Submission')
print(space(3))
print("   ## " + good.name + " Tab Breakdown"+ "  ##")
display(good_sort)

## Define Pivot (Piv) Function that pivots the discrepancy data, adds space, and adds a title
def piv(df_x):
    piv = df_x.groupby(['CaseName','CaseId','Submission','CaseUserDisplayName'])['Medicare Product Id'].count().reset_index()
    sort = piv.sort_values(['CaseUserDisplayName']).set_index('CaseName')
    if len(df_x) > 0:
        print(space(3))
        print("   ## " + df_x.name + " Tab Breakdown"+ "  ##")
        display (sort)
    else:
        pass

## Cycle through data frame list and apply the pivot function which also prints
for i in df_tab_lst:
    piv(i)

## Give some extra space at the bottom
print(space(2))


# ----------------------------------------


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('Pre 15th - To Look At File - ' + datex + '.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet (Master Exculded for now).

tab_loop_lst = [df, initquest, good, bad_clean, dupeSSN, genbad, datebad, newstage, noCDI]

def tab_write(df_y):
    if len(df_y) > 0:
        df_y.to_excel(writer,sheet_name = df_y.name, index = False)
    else:
        print (df_y.name + ' was not added to the spreadsheet because it was blank')

# Loop through the tab_lst and write to the writer.
for i in tab_loop_lst:
    tab_write(i)

# Close the  Excel writer and output the Excel file.
writer.save()