import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import copy
import csv
import os

#How to run this Coffeegame file in spyder with anaconda
#1 First make sure that the zip file is selected the directory
#2 Then open the google spreadsheets (that is the connection with the excel file)
#3 Then make sure to import the right packages gspread and oauth2client.service_account. If the packages are not installed, open the anacondapromp and use pip install function )code: pip install oauth2client and pip install gspread) 
#4 Run the file in spyder with anaconda!

#Connect to Google Sheets API 
def get_data_from_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    #Load service account credentials from API (make sure that the JSON key is correct)
    credentials = ServiceAccountCredentials.from_json_keyfile_name("mystery-coffee.json", scope)
    
    #Autorise and connect to Google Sheets
    client = gspread.authorize(credentials)

    #Open the correct Google Sheet
    sheet = client.open("Mystery coffee participants")
    # Haal alle gegevens op en zet ze in een Pandas DataFrame
    participants_data = sheet.get_worksheet(0)
    participants_data = participants_data.get_all_records()
    participants_data = pd.DataFrame(participants_data)
    
    # Retrieve all records and put them in a Pandas DataFrame
    icebreaker = sheet.get_worksheet(1)
    icebreaker = icebreaker.get_all_records()
    icebreaker_data = pd.DataFrame(icebreaker)
    
    return participants_data, icebreaker_data

#Filepaths to save the groups 
new_groups_txt = "Coffee_Partner_Lottery_new_groups.txt"
new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

#Load earlier groups to make sure there are not groups with the same people
opairs = set()
DELIMITER = ','

# Retrieve icebreaker and participant data
participants_data, icebreaker_data = get_data_from_sheets()

if os.path.exists(all_groups_csv):
    with open(all_groups_csv, "r") as file:
        csvreader = csv.reader(file, delimiter=DELIMITER)
        for row in csvreader:
            opairs.add(tuple(row))

# Check if the right columns are in the Google Sheet that is connected with the API
if "First name" not in participants_data.columns or "e-mail" not in participants_data.columns:
    raise ValueError("The google sheet has to consist 'First name' and'e-mail'")

#Make a list with unique participants based on e-mail
participants = list(set(participants_data["e-mail"]))

#Make a list with the icebreakers
icebreakers = list(set(icebreaker_data["Icebreakers"]))

#Diffent possible group sizes are made
group_sizes = [2, 3, 4, 5]

#Set to safe new groups 
ngroups = set()

#Copy of the participantlist to modify 
nparticipants = copy.deepcopy(participants)

# Copy of the ice breakers list to edit
nicebreakers = copy.deepcopy(icebreakers)

#Random groupsizes are made
while len(nparticipants) > 0:
    #Makes sure that there are always possible groupsizes present
    valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
    if not valid_sizes:
        break  # Stop als er geen geschikte groepsgroottes zijn

    #Chooses random groupsizes from the valid sizes
    group_size = random.choice(valid_sizes)
    
    #Selects a random participants for a group 
    group = random.sample(nparticipants, group_size)
    
    #When the participant is chosen it will remove this person from the list so the person will not be chosen again
    for person in group:
        nparticipants.remove(person)
    
    #Choose random icebreaker from the icebreaker list
    icebreaker_question = random.choice(icebreakers) if icebreakers else "No question to break the ice"

    # Voeg de groep toe aan de set met groepen en de icebreaker
    ngroups.add((tuple(group), icebreaker_question))

# Als er 1 persoon overblijft, voeg ze toe aan een bestaande groep
if len(nparticipants) == 1:
    leftover = nparticipants.pop()
    if ngroups:  # Zorg dat er een groep is om toe te voegen
        random_group = random.choice(list(ngroups))
        new_group = tuple(sorted(list(random_group[0]) + [leftover]))
        ngroups.remove(random_group)
        icebreaker_question = random_group[1]
        ngroups.add((new_group, icebreaker_question))

#Makes output for printen and saving
output_string = "------------------------\n"
output_string += "Today's Coffee Groups:\n"
output_string += "------------------------\n"

# Begin with i = 1 (refers to first group)
i = 1
for group_tuple in ngroups:
    group, icebreaker_question = group_tuple
    names = [participants_data[participants_data["e-mail"] == email].iloc[0]["First name"] for email in group]
    output_string += f"Group {i} " + ", ".join(f"  {name} ({email})" for name, email in zip(names, group)) + "\n"
    # Adding in the output the ice breaker with a tab for more clarity
    output_string += "    "  + "* "+ f"  A question to break the ice for group {i}: {icebreaker_question}\n"
    # With each new group make sure the number counts up
    i += 1
    
# Print the output
print(output_string)

#Saves to a textfile
with open(new_groups_txt, "w", encoding="utf8") as file:
    file.write(output_string)

#Safe groups to csv-file
with open(new_groups_csv, "w", encoding="utf8") as file:
    header = ["name1", "email1", "name2", "email2", "name3", "email3", "name4", "email4", "name5", "email5"]
    file.write(DELIMITER.join(header) + "\n")
    
    for group_tuple in ngroups:
        group = group_tuple[0]
        names = [participants_data[participants_data["e-mail"] == email].iloc[0]["First name"] for email in group]
        row = []
        for i in range(5):  # Maximaal 5 leden per groep
            if i < len(group):
                row.extend([names[i], group[i]])
            else:
                row.extend(["", ""])  # Lege cellen als de groep kleiner is dan 5
        file.write(DELIMITER.join(row) + "\n")

#Safe file to historical file so there will not be the same links
with open(all_groups_csv, "a", encoding="utf8") as file:
    for group_tuple in ngroups:
        file.write(DELIMITER.join(group_tuple[0]) + "\n")

print("\n New coffee groups are assigned. Have fun!")
