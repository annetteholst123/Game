def preprocessing(z):

    # Using global data frame, since without this the dataframe won't change
    global df
    
    # Count unique values of tye of bankruptcy
    type_bankruptcy = z.value_counts('TypeOfBankruptcy')
    print(f"The types of bankruptcy businesses are as followed: {type_bankruptcy}")
    
    # Count unique values of regions (output not shown here, because there are many reasons)
    # regions = df.value_counts('Regions')
    # print(regions)
    # Renaming types of bankruptcies
    z = z.replace('A028820','only_sole_prop')
    z = z.replace('A047596','total')
    z = z.replace('A047597','without_sole_prop') 
    
    # Check if succeeded
    type_bankruptcy = z.value_counts('TypeOfBankruptcy')
    print(f"\nThe types have been converted into more descriptive labels that reflect the actual bankruptcy categories: {type_bankruptcy}")
    # Pre-define variables
    i = 20
    t = 0

    # List of provinces
    list = ['Groningen', 'Fryslan', 'Drenthe', 'Overijssel', 'Flevoland', 'Gelderland', 'Utrecht', 'Noord-Holland', 'Zuid-Holland', 'Zeeland', 'Noord-Brabant', 'Limburg']

    # For-loop to replace provinces indexes with names
    for i in range(20,32):
        z = z.replace(f'PV{i}  ',f'{list[t]}')
        t = t + 1
    return z
    # Check if it worked
    # regions = df.value_counts('Regions')
    # print(regions)