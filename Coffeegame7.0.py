# -*- coding: utf-8 -*-

# Import library
import os
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

# Connect to Google Sheets API
def get_data_from_sheets():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    # Load service account credentials from API (make sure that the JSON key is correct)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "EspressYoSelf.json", scope)

    # Autorise and connect to Google Sheets
    client = gspread.authorize(credentials)

    # Open the correct Google Sheet
    sheet = client.open("EspressYo Self participants")
    # Retrieve all records of the participants and put them in a Pandas DataFrame
    data = sheet.get_worksheet(0)
    data = data.get_all_records()
    data = pd.DataFrame(data)
    # Retrieve all icebreakers and put them in a Pandas DataFrame
    icebreaker = sheet.get_worksheet(1)
    icebreaker = icebreaker.get_all_records()
    icebreaker_data = pd.DataFrame(icebreaker)
    
    # Upon calling the function, return the data of the participants and the icebreakers
    return data, icebreaker_data, sheet

# Retrieve icebreaker and participant data
data, icebreaker_data, sheet = get_data_from_sheets()

# Pre-defining empty dataframe
empty = pd.DataFrame()
# Replace empty rows with NaN values
cleaned_data = data.replace("", np.nan)
# Remove empty rows
cleaned_data = cleaned_data.dropna()

# Create a backup datasheet in the Google Sheet with all the current participants
def backup_datasheet(sheet):
    # Access the first worksheet correctly
    worksheet = sheet.get_worksheet(0)
    # Retrieve all the data as a list of lists
    data = worksheet.get_all_values()
    # Check if there is data in the Google Sheet
    if data:
        backup_datasheet_title = "EspressYoSelf_Backup"
        # Try to open the backup Google Sheet, if not possible create a new one
        try:
            backup_datasheet = sheet.worksheet(backup_datasheet_title)
        except gspread.exceptions.WorksheetNotFound:
            backup_datasheet = sheet.add_worksheet(title=backup_datasheet_title, rows=len(data), cols=len(data[0]))  # Create backup
            # Clear old backup
            backup_datasheet.clear()
            #save the new backup
            data = backup_datasheet.update("A1", data)
            print("Backup created successfully!")
    else:
        print("No data found to back up.")       

# Function to restore the data with the help of backup sheet
def restore_from_backup(sheet):
    try:
        # Open backup sheet
        backup_sheet = sheet.worksheet("EspressYoSelf_Backup")
        # Retrieve all the data
        backup_data = backup_sheet.get_all_values() 

        if backup_data:
            # Access main sheet
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

# Function to save the Output to a file
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
        os.startfile(filename)
    except Exception as e:
        print(f"error saving output to file {e}")

def group_forming():
    # If there's (less than) two participants
    if len(data) <= 2:
        print("There is not enough participants saved. You need a minimum of three participants. Make sure to fill in the Google forms first. \nIf you've previously used this matching game, a back-up has been stored. \nRun the game again to use back-up if needed.")
    else:
        # Filepaths to save the groups
        new_groups_txt = "Coffee_Partner_Lottery_new_groups.txt"
        new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
        all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

        # Load earlier groups to make sure there are not groups with the same people
        opairs = set()
        DELIMITER = ','

        if os.path.exists(all_groups_csv):
            with open(all_groups_csv, "r") as file:
                csvreader = csv.reader(file, delimiter=DELIMITER)
                for row in csvreader:
                    opairs.add(tuple(row))
    
        # Check if the right columns are in the Google Sheet that is connected with the API
        if "First name" not in data.columns or "E-mailaddress" not in data.columns or "Last name" not in data.columns:
            raise ValueError(
                "The google sheet has to contain the following personal information of the participants: \n'First name', 'Last name' and 'E-mailaddress'")

        # Make a list with unique participants based on e-mail
        # We chose e-mailaddress instead of the combination of first and last name,
        # since e-mailadresses are per definition unique. Someone could have the
        # exact same name, however the e-mailaddress should still be different.
        participants = list(set(data["E-mailaddress"]))

        # Make a list with the icebreakers
        icebreakers = list(set(icebreaker_data["Icebreakers"]))

        # Diffent possible group sizes are made
        group_sizes = [2, 3, 4, 5]

        # Set to safe new groups
        ngroups = set()

        # Copy of the participantlist to modify
        nparticipants = copy.deepcopy(participants)

        # Copy of the ice breakers list to edit
        nicebreakers = copy.deepcopy(icebreakers)

        # Random groupsizes are made
        while len(nparticipants) > 0:
            # Makes sure that there are always possible groupsizes present
            valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
            if not valid_sizes:
                break  # Stop when the group sizes aren't contained in the possible group sizes

            # Chooses random groupsizes from the valid sizes
            group_size = random.choice(valid_sizes)

            # Selects a random participants for a group
            group = random.sample(nparticipants, group_size)

            # When the participant is chosen it will remove this person from the list so the person will not be chosen again
            for person in group:
                nparticipants.remove(person)

            # Choose random icebreaker from the icebreaker list
            icebreaker_question = random.choice(
                icebreakers) if icebreakers else "No question to break the ice"

            # Add the group and the icebreaker to the set of groups
            ngroups.add((tuple(group), icebreaker_question))

        # If one participants is remaining groupless, add this person to an existing group
        if len(nparticipants) == 1:
            leftover = nparticipants.pop()
            if ngroups:  # Zorg dat er een groep is om toe te voegen
                random_group = random.choice(list(ngroups))
                new_group = tuple(sorted(list(random_group[0]) + [leftover]))
                ngroups.remove(random_group)
                icebreaker_question = random_group[1]
                ngroups.add((new_group, icebreaker_question))

        # Makes output for printen and saving
        output_string = "------------------------\n"
        output_string += "Today's groups are:\n"
        output_string += "------------------------\n"

        # Begin with i = 1 (start with counting by group 1; not group 0)
        i = 1
        for group_tuple in ngroups:
            group, icebreaker_question = group_tuple
            names = [(data[data["E-mailaddress"] == email].iloc[0]["First name"],
                  data[data["E-mailaddress"] == email].iloc[0]["Last name"]) for email in group]
            output_string += f"Group {i}: " + ", ".join(
                f"{name[0]} {name[1]} ({email})" for name, email in zip(names, group)) + "\n"
            # Adding in the output the ice breaker with a tab for more clarity
            output_string += "\t* " + \
                f"  A question to break the ice for group {i}: {icebreaker_question}\n" + "\n"
            # With each new group make sure the number counts up
            i += 1

        # Print the output
        print(output_string)

        # Saves formatted output to a file
        save_output_to_file(output_string, "EspressYoSelf_Groups.txt")

        # Safe groups to csv-file
        with open(new_groups_csv, "w", encoding="utf8") as file:
            header = ["name1", "email1", "name2", "email2", "name3",
                      "email3", "name4", "email4", "name5", "email5"]
            file.write(DELIMITER.join(header) + "\n")
        
            for group_tuple in ngroups:
                group = group_tuple[0]
                names = [(data[data["E-mailaddress"] == email].iloc[0]["First name"],
                          data[data["E-mailaddress"] == email].iloc[0]["Last name"]) for email in group]
                row = []
                for i in range(5):  # Maximum of five members per group
                    if i < len(group):
                        row.extend([f"{names[i][0]} {names[i][1]}", group[i]])
                    else:
                        # Empty cells if the group exists out of less than five participants
                        row.extend(["", ""])
                        file.write(DELIMITER.join(row) + "\n")

        # Safe file to historical file so there will not be the same links
        with open(all_groups_csv, "a", encoding="utf8") as file:
            for group_tuple in ngroups:
                file.write(DELIMITER.join(group_tuple[0]) + "\n")
        # Not contained in the for-loop otherwise the message is printed as many times as there are groups
        print("\n New groups are assigned. Have fun!") 

# Check if the participant sheet is empty
while data.empty:
    # Pre-defining user input
    user_input = ""
    # List of possible answers
    answers = ["y", "n"]
    # If users' input is not contained in answers
    while user_input not in answers:
        user_input = input("The data set is empty. Do you want to use the last saved back-up version? (y/n)")
        if user_input == "y":
            backup_datasheet(sheet)
            restore_from_backup(sheet)
            # Refresh data after restoring it
            data, icebreaker_data, sheet = get_data_from_sheets()
            # If the data is restored and thus not empty, call the group forming function
            if not data.empty:
                group_forming()
                # Prevent infinitely looping
                break
        # If user doesn't want to use the back-up
        else:
            # If user entered "n", then the user will be transported out of this loop and to the next if-statement
            break
    # If user doesn't want to use the back-up
    if user_input == "n":
        print("Please fill in participants' information to start this EspressYo Self matching game.")
        # Prevent infinitely looping
        break 
# If the sheet is not empty
else:
    # Renaming column names if the column names aren't already this
    data.columns.values[1] = "First name"
    data.columns.values[2] = "Last name"
    data.columns.values[3] = "E-mailaddress"
    # Pre-defining user input
    user_input = ""
    # List of possible answers
    answers = ["y", "n"]
    # Gives user the option to remove all data (if wanted)
    # We created this possibility of cleaning the data set, so this game can be used for different courses.
    # Starting with a clean data set would also be nice if the course is taken the next year, 
    # so the previous students' information will be removed and not included in the groups.
    while user_input not in answers:
        user_input = input("Do you want to clean all participants' data and start again? (y/n)")
        # If user wants to clean all data
        if user_input == "y":
            user_input = ""
            while user_input not in answers:
                # Offer the option to restore the datasheet with the help of backup if delted by accident
                user_input = input("This means that all participants' data will be removed. Do you want all data to be removed? (y/n)")
                # If user confirms to want to remove all data
                if user_input == "y":    
                    # Saving the back-up
                    backup_datasheet(sheet)
                    # Empties the dataframe
                    data = empty
                    # Replace empty rows with NaN values
                    data = data.replace("", np.nan)
                    # Remove empty rows
                    data = data.dropna()
                    # Access main sheet
                    worksheet = sheet.get_worksheet(0)
                    # Empties the participants' data in the Google spreadsheet
                    worksheet.clear()
                    # Updates the worksheet; writes the cleaned dataframe to a sheet
                    worksheet.update([data.columns.values.tolist()] + data.values.tolist())
                    print("Data cleaning is finalized. A back-up is stored just in case. Run the game again if you want to play.") 
                    # Prevent from infinitely looping
                    break
                # If user doesn't want to remove all data
                elif user_input == "n":
                    print("No data will be removed.")
                    group_forming()
                # Loops untill one of the possible answers is given
                else:
                     print("Please enter a valid option.")
        # If user doesn't want to clean all data
        elif user_input == "n":
            print("The group formation process will be continued.")
            group_forming()
        # When user' answer differs from "y" or "n" 
        else:
            print("Please enter a valid option.")
