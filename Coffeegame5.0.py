# Import libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import copy
import csv
import os

# How to run this Meetcute game file in spyder with anaconda
# 1 First make sure the EspressYo Self matching game zip file is selected in the directory, so that it can read all files
# 2 Then open the google spreadsheets (that is the connection with the excel file)
# 3 Fill in the Google forms with participant data if need be (the google forms is linked to the spreadsheet and will be updated automatically)
# 4 Then make sure to import the right packages gspread and oauth2client.service_account. If the packages are not installed, open the anacondapromp and use pip install function )code: pip install oauth2client and pip install gspread)
# 5 Run the file in spyder with anaconda!

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

# Pre-defining variable empty
empty = pd.DataFrame()

# Replace empty rows with NaN values
cleaned_data = data.replace("", float("NaN"))
# Remove empty rows
cleaned_data = cleaned_data.dropna()

# Check if the participant sheet is empty
while data.empty:
    print("Please fill in participants' name to start this EspressYo Self matching game.")
    # Prevent from infinitely iterating the loop
    break
# If the sheet is not empty
else:
    user_input = ""
    answers = ["y", "n"]
    # Gives user the option to remove all data (if needed)
    while user_input not in answers:
        user_input = input("Do you want to clean all participants' data and start again? (y/n)")
        if user_input == "y":
            print("All participants' data will be removed.")
            # Retrieves the participants' data
            worksheet = sheet.get_worksheet(0)
            # Empties the dataframe
            data = empty
            # Replace empty rows with NaN values
            cleaned_data = data.replace("", float("NaN"))
            # Remove empty rows
            cleaned_data = cleaned_data.dropna()
            # Empties the participants' data in the Google spreadsheet
            worksheet.clear()
            # Updates the worksheet
            worksheet.update([cleaned_data.columns.values.tolist()] + cleaned_data.values.tolist())
            
        elif user_input == "n":
            print("The group formation process will be continued.")
        else:
            print("Please enter a valid option.")

if len(cleaned_data) <= 2:
    print("There is not enough participants saved. You need a minimum of three participants. Make sure to fill in the Google forms first.")
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
            break  # Stop als er geen geschikte groepsgroottes zijn

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

    # Begin with i = 1 (refers to first group)
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

    # Saves to a textfile
    with open(new_groups_txt, "w", encoding="utf8") as file:
        file.write(output_string)

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
            for i in range(5):  # Maximaal 5 leden per groep
                if i < len(group):
                    row.extend([f"{names[i][0]} {names[i][1]}", group[i]])
                else:
                    # Lege cellen als de groep kleiner is dan 5
                    row.extend(["", ""])
                    file.write(DELIMITER.join(row) + "\n")

    # Safe file to historical file so there will not be the same links
    with open(all_groups_csv, "a", encoding="utf8") as file:
        for group_tuple in ngroups:
            file.write(DELIMITER.join(group_tuple[0]) + "\n")
            print("\n New groups are assigned. Have fun!")
