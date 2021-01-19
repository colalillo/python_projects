# DSIQ

###### 104 Return Alternating List (Highest-Lowest) of Numbers

# Inputs
arr = [10, 2, 11, 3, 7, 4, 1, 6, 15, 2, 5, 9, 8, 14, 12, 13, 17]
n = len(arr)

# Solution
def chapped_sort(arr, n):
    fin = []
    arr_s = sorted(arr)
    
    i = 0
    j = n-1
    
    while i < j:
        
        fin.append(j)
        j -= 1
        
        fin.append(i)
        i += 1
    
    if n % 2 != 0:
        s = n / 2
        s = int(s - 0.5)
        fin.append(s)
    
    return fin

chapped_sort(arr, n)



##### 1 Calculating percentage of fradulent transactions by day

# Inputs
df_01 = pd.DataFrame({
'Store_ID': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
'Date': ['01/01/2001', '01/01/2001', '01/01/2001', '01/01/2001', '02/01/2001', '02/01/2001', '02/01/2001', '02/01/2001', '03/01/2001', '03/01/2001', '03/01/2001', '03/01/2001'],
'Status': ['fraud', 'closed', 'fraud', 'open', 'open', 'closed', 'fraud', 'open', 'open', 'closed', 'fraud', 'open'],
'Revenue': [125, 220, 135, 240, 155, 160, 270, 180, 195, 210, 115, 125]
})

# Solution
analys = df_01[df_01.Revenue > 0]
analys['Fraudulent'] = analys['Status'] == 'fraud'
final = analys.groupby('Date').Fraudulent.mean()*100



###### 106 Sorting Pandas Dataframe by Caloric Density

# Inputs
raw_data = {'food': ['bacon', 'strawberries', 'banana', 'spinach', 'chicken breast', 'peanuts', 'cereal'], 
            'grams': [50, 200, 100, 200, 50, 100, 150],
           'calories': [271, 64, 89, 46, 80, 567, 271]}
dsx = pd.DataFrame(raw_data, columns = ['food', 'grams', 'calories'])

# Solution
dsx['density'] = dsx['calories'] / dsx['grams']
# stp = dsx.sort_values('density', ascending = False)
stp = dsx.sort_values(['calories', 'density'], ascending = [False, False], inplace = True)
