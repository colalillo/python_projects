# Import Dependencies
import pandas as pd
import os

from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# create engine, make connection to reporting DB
engine = create_engine(CaseNames.engine_var)
metadata = MetaData(bind=engine)

# create dataframe from table pulled from sql
df = pd.read_sql(
"""
select distinct Clientid as 'Client Id', Casename as 'Case Name', Tort, FirmName as 'Firm Name', ClientLastName as 'Last Name', ClientFirstName as 'First Name', ClientDOB as 'DOB', ClientDOD as 'DOD', clientssn as 'SSN', MedicareHicNumber as 'HICN #', OnBenefits as 'On Benefits', OnBenefitsVerified as 'On Benefits Verified', ClientDescriptionOfInjury as 'Desc of Injury',
	case
		when FinalizedStatusId = 1 then 'Pending Finalization'
		when FinalizedStatusId = 2 then 'Finalized'
		when FinalizedStatusId = 3 then 'Finalized'
		else 'Pending Finalization'
	end as 'Finalization Status',
	case 
		when FinalizedStatusName = 'Pending Finalized' then 'Claimant does not meet scope rules'
		when FinalizedStatusName = 'System Finalized' then 'All liens are final, scope rules met'
		when FinalizedStatusName = 'Agent Finalized' then 'LM has declared them final'
	else 'Claimant has Pending Liens'
	end as 'Finalization Notes',
	FinalGlobalAmount,
	case
		when (clientingestiondate is not NULL or clientingestiondate <> '') and (ClientInjuryDate is NULL or ClientInjuryDate = '') and (Surgery1 is NULL or Surgery1 = '') and (Surgery2 is NULL or Surgery2 = '') and (Surgery3 is NULL or Surgery3 = '') and (Surgery4 is NULL or Surgery4 = '') and (Surgery5 is NULL or Surgery5 = '') and (Surgery6 is NULL or Surgery6 = '') and (Surgery7 is NULL or Surgery7 = '') and (Surgery8 is NULL or Surgery8 = '') and (Surgery9 is NULL or Surgery9 = '') and (Surgery10 is NULL or Surgery10 = '') and (Surgery11 is NULL or Surgery11 = '') and (Surgery12 is NULL or Surgery12 = '') then 'Ingestion Date Only'
		else 'Not Ingestion Date Only'
	end as 'File',
	clientingestiondate as 'Ingestion Date', ClientInjuryDate as 'Injury Date', Surgery1 as 'Surgery01', Surgery2 as 'Surgery02', Surgery3 as 'Surgery03', Surgery4  as 'Surgery04', Surgery5 as 'Surgery05', Surgery6  as 'Surgery06', Surgery7 as 'Surgery07', Surgery8 as 'Surgery08', Surgery9 as 'Surgery09', Surgery10 as 'Surgery10', Surgery11, Surgery12
from FullProductViews
where lientype = 'medicare - global' and CaseName not like '%hold%' and CaseName not like '%closed' and (InactiveReasonName is null or InactiveReasonName  = 'resolved') and ismt = 1 and tort <> 'tvm'
""",
con = engine
)

# Identify the columns from the table that are pre-surgery
pre_surj_lst = ['Client Id', 'Case Name', 'Tort', 'Firm Name', 'Last Name', 'First Name', 'DOB', 'DOD', 'SSN', 'HICN #', 'On Benefits', 'On Benefits Verified', 'Desc of Injury', 'Finalization Status', 'Finalization Notes', 'FinalGlobalAmount', 'File']


# Separating Out Dataframes:
ing_only = df[df['File'] == 'Ingestion Date Only'].iloc[:,0:18].rename(columns = {'Ingestion Date':'Date'})
ing_only.insert(17, 'Surgery', 'Ingestion Only')

the_rest = df[df['File'] == 'Not Ingestion Date Only']


# Transpose data right of surgery onto a new line:
transposed = the_rest.melt(id_vars=pre_surj_lst, 
        var_name="Surgery", 
        value_name="Date")


# Add dataframes back together and remove unwanted rows of data:
full_df = pd.concat([transposed, ing_only])
zzz = full_df.sort_values(['Client Id','Surgery','Date'])
zz2 = zzz[zzz['Date'].isna() == False].drop_duplicates(subset = ['Client Id', 'Date'], keep='first')
zz2.to_excel('MCare Updated Report.xlsx', index = False)