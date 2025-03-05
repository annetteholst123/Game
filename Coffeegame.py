#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 22:04:07 2025

@author: annetteholst
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import copy
import csv
import os

# Google Sheets API connection function
def get_participant_data_from_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load service account credentials (Ensure JSON file is in your project directory)
    credentials = ServiceAccountCredentials.from_json_keyfile_name("mystery-coffee.json", scope)
    
    # Authenticate and connect to Google Sheets
    client = gspread.authorize(credentials)

    # Open Google Sheet by its name
    sheet = client.open("Mystery coffee participants").sheet1  # Replace with your actual sheet name

    # Fetch all rows as a list of dictionaries
    data = sheet.get_all_records()

    # Convert data to a Pandas DataFrame
    return pd.DataFrame(data)

# File paths
new_groups_txt = "Coffee_Partner_Lottery_new_groups.txt"
new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

# Load previous pairings to avoid duplicates
opairs = set()
DELIMITER = ','

if os.path.exists(all_groups_csv):
    with open(all_groups_csv, "r") as file:
        csvreader = csv.reader(file, delimiter=DELIMITER)
        for row in csvreader:
            opairs.add(tuple(row))

# Fetch participant data from Google Sheets
formdata = get_participant_data_from_sheets()

# Check if the data contains the required columns
if "First name" not in formdata.columns or "e-mail" not in formdata.columns:
    raise ValueError("Google Sheet must contain 'First name' and 'e-mail' columns!")

# Create a list of unique participants (email-based)
nparticipants = list(set(formdata["e-mail"]))

while len(nparticipants) > 0:
    # Ensure we are not selecting from an empty list
    valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
    if not valid_sizes:
        break  # If no valid group sizes, stop the loop

    group_size = random.choice(valid_sizes)  # Choose a group size from valid options
    
    # Select random participants for the group
    group = random.sample(nparticipants, group_size)
    
    # Remove them from the available participants list
    for person in group:
        nparticipants.remove(person)

    # Sort the group alphabetically for consistency
    group.sort()
    
    # Add the group to the new set
    ngroups.add(tuple(group))

# If only one participant is left, add them to an existing group
if len(nparticipants) == 1:
    leftover = nparticipants.pop()
    if ngroups:  # Ensure there's an existing group to add to
        random_group = random.choice(list(ngroups))  # Pick an existing group
        new_group = tuple(sorted(list(random_group) + [leftover]))
        ngroups.remove(random_group)
        ngroups.add(new_group)
    
# Initialize set for new groups
ngroups = set()

# Copy participants list to avoid modifying the original
nparticipants = copy.deepcopy(participants)

# Flag to track if new unique pairings are found
new_groups_found = False

# Choose group sizes (2, 3, 4, or 5)
group_sizes = [2, 3, 4, 5]

while len(nparticipants) > 0:
    # If only one participant is left, add them to an existing group
    if len(nparticipants) == 1:
        leftover = nparticipants.pop()
        if ngroups:  # Ensure there's an existing group to add to
            random_group = random.choice(list(ngroups))  # Pick an existing group
            new_group = tuple(sorted(list(random_group) + [leftover]))
            ngroups.remove(random_group)
            ngroups.add(new_group)
        break  # Stop loop since all participants are assigned

    # Ensure we are not selecting from an empty list
    valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
    if not valid_sizes:
        break  # If no valid group sizes, stop the loop

    group_size = random.choice(valid_sizes)  # Choose a group size from valid options
    
    # Select random participants for the group
    group = random.sample(nparticipants, group_size)
    
    # Remove them from the available participants list
    for person in group:
        nparticipants.remove(person)

    # Sort the group alphabetically for consistency
    group.sort()
    
    # Add the group to the new set
    ngroups.add(tuple(group))

    while len(nparticipants) > 0:
        # Randomly choose a group size (ensuring it's not bigger than remaining participants)
        group_size = random.choice([s for s in group_sizes if s <= len(nparticipants)])
        
        # Select random participants for the group
        group = random.sample(nparticipants, group_size)
        
        # Remove them from the available participants list
        for person in group:
            nparticipants.remove(person)
        
        # Sort the group alphabetically for consistency
        group.sort()
        
        # Add the group to the new set
        ngroups.add(tuple(group))

    # If someone is left out, add them to an existing group
    if len(nparticipants) > 0:
        leftover = nparticipants.pop()
        random_group = random.choice(list(ngroups))
        new_group = tuple(sorted(list(random_group) + [leftover]))
        ngroups.remove(random_group)
        ngroups.add(new_group)

    # Ensure no duplicate groupings from past rounds
    if ngroups.isdisjoint(opairs):
        new_groups_found = True

# Prepare output string for printing and saving
output_string = "------------------------\n"
output_string += "Today's Coffee Groups:\n"
output_string += "------------------------\n"

for group in ngroups:
    names = [formdata[formdata["e-mail"] == email].iloc[0]["First name"] for email in group]
    output_string += "* " + ", ".join(f"{name} ({email})" for name, email in zip(names, group)) + "\n"

# Print output
print(output_string)

# Save output to text file
with open(new_groups_txt, "w", encoding="utf8") as file:
    file.write(output_string)

# Save new groups to CSV file
with open(new_groups_csv, "w", encoding="utf8") as file:
    header = ["name1", "email1", "name2", "email2", "name3", "email3", "name4", "email4", "name5", "email5"]
    file.write(DELIMITER.join(header) + "\n")
    
    for group in ngroups:
        names = [formdata[formdata["e-mail"] == email].iloc[0]["First name"] for email in group]
        row = []
        for i in range(5):  # Handle groups of up to 5 members
            if i < len(group):
                row.extend([names[i], group[i]])
            else:
                row.extend(["", ""])
        file.write(DELIMITER.join(row) + "\n")

# Append groups to history file (to avoid repetition)
with open(all_groups_csv, "a", encoding="utf8") as file:
    for group in ngroups:
        file.write(DELIMITER.join(group) + "\n")

print("\nJob Done! New coffee groups have been assigned.")


