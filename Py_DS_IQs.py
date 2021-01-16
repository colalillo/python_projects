# DSIQ

## 106 Return Alternating List (Highest-Lowest) of Numbers

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