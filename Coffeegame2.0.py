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

# Google Sheets API verbinden
def get_participant_data_from_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Laad service account credentials (zorg ervoor dat het JSON-bestand correct is)
    credentials = ServiceAccountCredentials.from_json_keyfile_name("mystery-coffee.json", scope)
    
    # Autoriseer en maak verbinding met Google Sheets
    client = gspread.authorize(credentials)

    # Open de juiste Google Sheet
    sheet = client.open("Mystery coffee participants").sheet1  # Zorg dat de naam exact klopt!

    # Haal alle gegevens op en zet ze in een Pandas DataFrame
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Bestandspaden
new_groups_txt = "Coffee_Partner_Lottery_new_groups.txt"
new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

# Laad eerdere groepen om dubbele paren te vermijden
opairs = set()
DELIMITER = ','

if os.path.exists(all_groups_csv):
    with open(all_groups_csv, "r") as file:
        csvreader = csv.reader(file, delimiter=DELIMITER)
        for row in csvreader:
            opairs.add(tuple(row))

# Haal deelnemers op uit Google Sheets
formdata = get_participant_data_from_sheets()

# Controleer of de juiste kolommen in Google Sheets staan
if "First name" not in formdata.columns or "e-mail" not in formdata.columns:
    raise ValueError("De Google Sheet moet kolommen 'First name' en 'e-mail' bevatten!")

# Maak een lijst met unieke deelnemers (op basis van e-mail)
participants = list(set(formdata["e-mail"]))

# Mogelijke groepsgroottes (kan aangepast worden)
group_sizes = [2, 3, 4, 5]

# Set om nieuwe groepen op te slaan
ngroups = set()

# Kopie van de deelnemerslijst om te bewerken
nparticipants = copy.deepcopy(participants)

# Willekeurige groepsindeling maken
while len(nparticipants) > 0:
    # Zorg dat er altijd een mogelijke groepsgrootte is
    valid_sizes = [s for s in group_sizes if s <= len(nparticipants)]
    if not valid_sizes:
        break  # Stop als er geen geschikte groepsgroottes zijn

    # Kies willekeurig een groepsgrootte
    group_size = random.choice(valid_sizes)
    
    # Selecteer willekeurig deelnemers voor de groep
    group = random.sample(nparticipants, group_size)
    
    # Verwijder hen uit de lijst met beschikbare deelnemers
    for person in group:
        nparticipants.remove(person)

    # Sorteer de groep alfabetisch (voor consistentie)
    group.sort()
    
    # Voeg de groep toe aan de set met groepen
    ngroups.add(tuple(group))

# Als er 1 persoon overblijft, voeg ze toe aan een bestaande groep
if len(nparticipants) == 1:
    leftover = nparticipants.pop()
    if ngroups:  # Zorg dat er een groep is om toe te voegen
        random_group = random.choice(list(ngroups))
        new_group = tuple(sorted(list(random_group) + [leftover]))
        ngroups.remove(random_group)
        ngroups.add(new_group)

# Output maken voor printen en opslaan
output_string = "------------------------\n"
output_string += "Today's Coffee Groups:\n"
output_string += "------------------------\n"

for group in ngroups:
    names = [formdata[formdata["e-mail"] == email].iloc[0]["First name"] for email in group]
    output_string += "* " + ", ".join(f"{name} ({email})" for name, email in zip(names, group)) + "\n"

# Print de output
print(output_string)

# Opslaan naar een tekstbestand
with open(new_groups_txt, "w", encoding="utf8") as file:
    file.write(output_string)

# Opslaan naar een CSV-bestand
with open(new_groups_csv, "w", encoding="utf8") as file:
    header = ["name1", "email1", "name2", "email2", "name3", "email3", "name4", "email4", "name5", "email5"]
    file.write(DELIMITER.join(header) + "\n")
    
    for group in ngroups:
        names = [formdata[formdata["e-mail"] == email].iloc[0]["First name"] for email in group]
        row = []
        for i in range(5):  # Maximaal 5 leden per groep
            if i < len(group):
                row.extend([names[i], group[i]])
            else:
                row.extend(["", ""])  # Lege cellen als de groep kleiner is dan 5
        file.write(DELIMITER.join(row) + "\n")

# Toevoegen aan historisch bestand (voorkomen van herhaalde koppelingen)
with open(all_groups_csv, "a", encoding="utf8") as file:
    for group in ngroups:
        file.write(DELIMITER.join(group) + "\n")

print("\n Job Done! Nieuwe koffie groepen zijn ingedeeld.")

