# -*- coding: utf-8 -*-

# Import library
import os
import platform
import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import copy
import csv
import numpy as np

# How to run this EspressYo Self game file in spyder with the use of anaconda
# 1 First make sure to download the EspressYo Self zip file and make sure that the file is selected in the directory of spyder, so that it can read all files
# 2 Then open the google spreadsheets (that is the connection with the excel file)
# 3 Fill in the Google forms with participant data (the google forms is linked to the spreadsheet and will be updated automatically)
# 4 Then make sure to import the right packages gspread and oauth2client.service_account. If the packages are not installed, open the anacondapromp and use pip install function (code: pip install oauth2client and pip install gspread)
# 5 Now you can run the file in spyder with anaconda and it will form the groups and it will produce a txt file with the groups and a question to break the ice.

# The source used for (most of) the icebreakers is: https://www.mural.co/blog/icebreaker-questions.
# The icebreakers that are used for this project are to be found in the google spreadsheet that's linked with the API.
# The source used on how to make the API key and connect it to the spreadsheet (google forms) is: https://developers.google.com/sheets/api/scopes and https://stackoverflow.com/questions/51571487/how-to-use-the-scope-https-www-googleapis-com-auth-drive-file-correctlyc 
# https://developers.google.com/workspace/guides/create-credentials
# The source used for how to create random groups and that people are removed and used only once in the list is: https://ercanvural-bm.medium.com/how-to-build-random-team-generator-by-python-67a1724b3c09

# Connect to Google Sheets API
def get_data_from_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]

    #load service account credentials from API 
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "EspressYoSelf.json", scope)

    #autorise and connect to Google Sheets
    client = gspread.authorize(credentials)

    #open the correct Google Sheet
    sheet = client.open("EspressYo Self participants")
    #Gets all records of the participants and puts them in a Pandas DataFrame
    data = sheet.get_worksheet(0)
    data = data.get_all_records()
    data = pd.DataFrame(data)
    #get all icebreakers and put them in a Pandas DataFrame
    icebreaker = sheet.get_worksheet(1)
    icebreaker = icebreaker.get_all_records()
    icebreaker_data = pd.DataFrame(icebreaker)
    
    #After calling the function, return the data of the participants and the icebreakers
    return data, icebreaker_data, sheet

#get icebreaker and participant data
data, icebreaker_data, sheet = get_data_from_sheets()

#pre-defining empty dataframe
empty = pd.DataFrame()
#replace empty rows with NaN values
cleaned_data = data.replace("", np.nan)
#remove empty rows
cleaned_data = cleaned_data.dropna()

#create a backup datasheet in the Google Sheet with all the current participants
def backup_datasheet(sheet):
    #access the first worksheet correctly
    worksheet = sheet.get_worksheet(0)
    #get all the data as a list of lists
    data = worksheet.get_all_values()
    #check if there is data in the Google Sheet
    if data:
        backup_datasheet_title = "EspressYoSelf_Backup"
        #tries to open the backup Google Sheet, if not possible creates a new one
        try:
            backup_datasheet = sheet.worksheet(backup_datasheet_title)
        except gspread.exceptions.WorksheetNotFound:
            backup_datasheet = sheet.add_worksheet(title=backup_datasheet_title, rows=len(data), cols=len(data[0]))  # Create backup
            #clears old backup
            backup_datasheet.clear()
            #save the new backup
            data = backup_datasheet.update("A1", data)
            print("Backup created successfully!")
    else:
        print("No data found to back up.")       

#function to restore the data with the help of backup sheet
def restore_from_backup(sheet):
    try:
        #open backup sheet
        backup_sheet = sheet.worksheet("EspressYoSelf_Backup")
        #gets all the data
        backup_data = backup_sheet.get_all_values() 

        if backup_data:
            #access main sheet
            worksheet = sheet.get_worksheet(0)  
            # Clear the current data before restoring it
            worksheet.clear() 
            # Restore the data
            worksheet.update("A1", backup_data) 
            print("Data successfully restored from backup.")

        else:
            print("No backup data found.")
    except gspread.exceptions.WorksheetNotFound:
        print("No backup sheet found. Cannot restore data.")    
        
#creating a cross-platform function to be able to open txt file
def open_file(filename):
    #create the function for windows
    if platform.system() == "Windows":
        os.startfile(filename)
    #create the function for macOS
    elif platform.system() == "Darwin":
        subprocess.call(["open", filename])
    #create the function for Linux and any other OS
    else:
        subprocess.call(["xdg-open", filename])
        
#function to save the Output to a file
def save_output_to_file(output_string, filename="EspressoYoSelf_Groups.txt"):
    try:
        with open(filename, "w", encoding="utf8") as file:
            file.write("-------------------------\n")
            file.write("  EspressYo Self Groups  \n")
            file.write("-------------------------\n\n")
            file.write(output_string)
            file.write("\n-------------------------\n")
            file.write("New groups are assigned. Have fun!\n")
            file.write("-------------------------\n")
        print(f"Groups have been saved to '{filename}'")
        open_file(filename)
    except Exception as e:
        print(f"error saving output to file {e}")

def group_forming():
    #ff there is (less than) two participants
    if len(data) <= 2:
        print("There is not enough participants saved. You need a minimum of three participants. Make sure to fill in the Google forms first. \nIf you've previously used this matching game, a back-up has been stored. \nRun the game again to use back-up if needed.")
    else:
        #filepaths to save the groups
        new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
        all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

        #will load earlier groups to make sure there are not groups with the same people
        opairs = set()
        DELIMITER = ','

        if os.path.exists(all_groups_csv):
            with open(all_groups_csv, "r") as file: #the csv file will be opened in read mode
                csvreader = csv.reader(file, delimiter=DELIMITER)
                for row in csvreader:
                    opairs.add(tuple(row))
    
        # Check if the right columns are in the Google Sheet that is connected with the API
        if "First name" not in data.columns or "E-mailaddress" not in data.columns or "Last name" not in data.columns:
            raise ValueError(
                "The google sheet has to contain the following personal information of the participants: \n'First name', 'Last name' and 'E-mailaddress'")

        #make a list with unique participants based on e-mail
        #we chose e-mailaddress instead of the combination of first and last name,
        #since e-mailadresses are per definition unique. Someone could have the
        #exact same name, however the e-mailaddress should still be different.
        participants = list(set(data["E-mailaddress"]))

        #will make a list with the icebreakers
        icebreakers = list(set(icebreaker_data["Icebreakers"]))

        #diffent group sizes are made (2,3,4 and 5)
        group_sizes = [2, 3, 4, 5]

        #set for saving new groups
        ngroups = set()

        #copy of the participant list to modify
        nparticipants = copy.deepcopy(participants)

        #random groupsizes are made
        while len(nparticipants) > 0: #will run as long there are still participants left in nparticipants
            #this makes sure that there are always possible groupsizes present
            valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
            if not valid_sizes:
                break  # Stop when the group sizes are no in the possible group sizes

            #chooses random groupsizes from the valid sizes
            group_size = random.choice(valid_sizes)

            #selects a random participants for a group
            group = random.sample(nparticipants, group_size)

            #when the participant is chosen it will remove this person from the list so the person will not be chosen again
            for person in group:
                nparticipants.remove(person)

            #chooses random icebreaker from the icebreaker list
            icebreaker_question = random.choice(
                icebreakers) if icebreakers else "No question to break the ice"

            #will add the group and the icebreaker to the set of groups
            ngroups.add((tuple(group), icebreaker_question))

        #if one participants is remaining groupless, add this person to an existing group
        if len(nparticipants) == 1:
            leftover = nparticipants.pop()
            if ngroups:  #makes sure that there is a group to add to
                random_group = random.choice(list(ngroups))
                new_group = tuple(sorted(list(random_group[0]) + [leftover]))
                ngroups.remove(random_group)
                icebreaker_question = random_group[1]
                ngroups.add((new_group, icebreaker_question))

        #makes output for printing and saving
        output_string = "------------------------\n"
        output_string += "Today's groups are:\n"
        output_string += "------------------------\n"

        #will start with i = 1 (start with counting by group 1 and not group 0)
        i = 1
        for group_tuple in ngroups:
            group, icebreaker_question = group_tuple
            names = [(data[data["E-mailaddress"] == email].iloc[0]["First name"],
                  data[data["E-mailaddress"] == email].iloc[0]["Last name"]) for email in group]
            output_string += f"Group {i}: " + ", ".join(
                f"{name[0]} {name[1]} ({email})" for name, email in zip(names, group)) + "\n"
            #adding in the output the ice breaker with a tab for more clarity
            output_string += "\t* " + \
                f"  A question to break the ice for group {i}: {icebreaker_question}\n" + "\n"
            #with each new group make sure the number counts up and not down
            i += 1

        #print the output
        print(output_string)

        #saves formatted output to a file
        save_output_to_file(output_string, "EspressYoSelf_Groups.txt")

        #safe groups to csv-file
        with open(new_groups_csv, "w", encoding="utf8") as file:
            header = ["name1", "email1", "name2", "email2", "name3",
                      "email3", "name4", "email4", "name5", "email5"]
            file.write(DELIMITER.join(header) + "\n")
        
            for group_tuple in ngroups:
                group = group_tuple[0]
                names = [(data[data["E-mailaddress"] == email].iloc[0]["First name"],
                          data[data["E-mailaddress"] == email].iloc[0]["Last name"]) for email in group]
                row = []
                for i in range(5):  #maximum of five members per group
                    if i < len(group):
                        row.extend([f"{names[i][0]} {names[i][1]}", group[i]])
                    else:
                        #empty cells if the group exists out of less than five participants
                        row.extend(["", ""])
                        file.write(DELIMITER.join(row) + "\n")

        #safe file to historical file so there will not be the same links
        with open(all_groups_csv, "a", encoding="utf8") as file:
            for group_tuple in ngroups:
                file.write(DELIMITER.join(group_tuple[0]) + "\n")
        #not contained in the for-loop otherwise the message is printed as many times as there are groups
        print("\n New groups are assigned. Have fun!") 

#using a flag to see if the data has already been restored using the backup
restored = False
#checks to see if the participant sheet is empty and has not been rosted using the backup
while data.empty and not restored:
    #pre-defining user input
    user_input = ""
    #list of possible answers
    answers = ["y", "n"]
    #if users' input is not contained in answers
    while user_input not in answers:
        user_input = input("The data set is empty. Do you want to use the last saved back-up version? (y/n)")
        if user_input == "y":
            backup_datasheet(sheet)
            restore_from_backup(sheet)
            #refresh data after restoring it
            data, icebreaker_data, sheet = get_data_from_sheets()
            #if the data is restored and thus not empty, call the group forming function
            if not data.empty:
                group_forming()
                #prevents infinitely looping and set the restored flag to true
                restored = True
                break
        #if user does not want to use the back-up
        else:
            #if user entered "n", then the user will be transported out of this loop and to the next if-statement
            break
    #if user doesn't want to use the back-up
    if user_input == "n":
        print("Please fill in participants' information to start this EspressYo Self matching game.")
        #prevents infinitely looping
        break 
#if the sheet is not empty and has not been restored using backup
else:
    if not restored:
        #renaming column names if the column names are not already this
        data.columns.values[1] = "First name"
        data.columns.values[2] = "Last name"
        data.columns.values[3] = "E-mailaddress"
        #pre defining user input
        user_input = ""
        #list of possible answers
        answers = ["y", "n"]
        #gives user the option to remove all data (if wanted)
        #we created this possibility of cleaning the data set, so this game can be used for different courses.
        #starting with a clean data set would also be nice if the course is taken the next year, 
        # so the previous students' information will be removed and not included in the groups.
        while user_input not in answers:
            user_input = input("Do you want to clean all participants' data and start again? (y/n)")
            # If user wants to clean all data
            if user_input == "y":
                user_input = ""
                while user_input not in answers:
                    #offers the option to restore the datasheet with the help of backup if delted by accident
                    user_input = input("This means that all participants' data will be removed. Do you want all data to be removed? (y/n)")
                    # if user confirms to want to remove all data
                    if user_input == "y":    
                        #saving the back-up
                        backup_datasheet(sheet)
                        #empties the dataframe
                        data = empty
                        #replaces empty rows with NaN values
                        data = data.replace("", np.nan)
                        #remove empty rows
                        data = data.dropna()
                        #access main sheet
                        worksheet = sheet.get_worksheet(0)
                        #empties the participants' data in the Google spreadsheet
                        worksheet.clear()
                        #updates the worksheet; writes the cleaned dataframe to a sheet
                        worksheet.update([data.columns.values.tolist()] + data.values.tolist())
                        print("Data cleaning is finalized. A back-up is stored just in case. Run the game again if you want to play.") 
                        #prevents from infinitely looping
                        break
                    #if user does nor want to remove all data
                    elif user_input == "n":
                        print("No data will be removed.")
                        group_forming()
                        #will loop untill one of the possible answers is given
                    else:
                        print("Please enter a valid option.")
            #if user does not want to clean all data
            elif user_input == "n":
                print("The group formation process will be continued.")
                group_forming()
            #when user' answer differs from "y" or "n" 
            else:
                print("Please enter a valid option.")
