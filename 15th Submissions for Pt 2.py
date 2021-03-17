
# Import dependencies:
import pandas as pd
import os
from datetime import datetime
import CaseNames # another python file I don't want on github


# Establishing Date
datex = datetime.now().strftime("%Y-%m-%d")
datey = datetime.now().strftime("%m/%d/%Y")


# Reimport edited file:
edited = pd.read_excel('Pre 15th - To Look At File - ' + datex + '.xlsx', sheet_name = '- To Submit -')

# Create a list with all of the unique entries in the Submission column:
splt_lst = edited.Submission.unique()

# If it's a reverification file it will split up the edited dataframe, export it, and edit the file name.
# If it's not a reverification it will split up the edited dataframe by other submissiions and edit the file name.
rever_str = str()
init_str = str()

for i in splt_lst:
    if i in CaseNames.rever_lst:
        x = edited[edited["Submission"] == i].iloc[:,4:9]
        x.to_excel("Archer-Shapiro - Auth - " + i + " - Reverification - " + datex + ".xlsx", index = False)
        rever_str += i + '\n'
    else:
        y = edited[edited["Submission"] == i].iloc[:,4:9]
        y.to_excel("Archer-Shapiro - No Auth - TVM - " + i +" - Claimant Universe - " + datex + ".xlsx", index = False)
        init_str += i + '\n'


# Pushed lien file for co-workers to reference:
push_data = edited[['SSN', 'Medicare Product Id', 'ClientId', 'Last Name', 'First Name', 'Date of Birth', 'Gender', 'CaseName', 'CaseId', 'Stage', 'ClientDrugIngested', 'Submission']]
push_data.to_excel('Post 15th Push Data for team members.xlsx', index = False)

### Create Push file to drop in SLAM: ###

# Select only the two columns that matter:
stagepush = push_data[['Medicare Product Id','Submission']].rename(columns = {'Medicare Product Id':'Id'})
# stagepush.rename(columns = {'Medicare Id':'Id'})

# Add two easy columns:
stagepush['SubmittedtoCMSDate'] = datey
stagepush['NewLienNote'] = 'Sent via global submission to CMS for EV'

# Add a column with stage EV if on reverification list otherwise stage of EVPSC:
is_evpsc = lambda x: 'Entitlement Verification' if x in (CaseNames.rever_lst) else 'Entitlement Verification/Pending Submission Confirmation'
stagepush['Stage'] = stagepush.Submission.apply(is_evpsc)

# Remove unnecessary columns and create:
pushfinal = stagepush[['Id', 'Stage', 'SubmittedtoCMSDate', 'NewLienNote', 'Submission']]
pushfinal.to_csv('Post 15th Push.csv', index = False)

# Create Email Text:
email_txt ="Hi everyone," + "\n" + "\n" + "I've created the submissions for the 15th. \
The spreadsheets are attached with the same password as always, and there's a list \
of them below. They can also be found in the following location:" + "\n" + "\n" \
+ "F:\Mass Tort Cases\Medicare spreadsheets\Internal\Submissions (15th)" + "\n" + "\n" \
+ "Reverification Submissions:" + "\n" + rever_str + "\n" + "Initial Submissions:" \
+ "\n" + init_str + "\n" + "If you have any questions or concerns, please let me know." \
+ "\n" + "\n" + "Thanks," + "\n" + "\n" + "Richard"
print(email_txt)
    