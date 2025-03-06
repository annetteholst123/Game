import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random
import copy
import csv
import os

# Google Sheets API verbinden
def get_data_from_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Laad service account credentials (zorg ervoor dat het JSON-bestand correct is)
    credentials = ServiceAccountCredentials.from_json_keyfile_name("mystery-coffee.json", scope)
    
    # Autoriseer en maak verbinding met Google Sheets
    client = gspread.authorize(credentials)

    # Open de juiste Google Sheet
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

# Bestandspaden
new_groups_txt = "Coffee_Partner_Lottery_new_groups.txt"
new_groups_csv = "Coffee_Partner_Lottery_new_groups.csv"
all_groups_csv = "Coffee_Partner_Lottery_all_groups.csv"

# Laad eerdere groepen om dubbele paren te vermijden
opairs = set()
DELIMITER = ','

# Retrieve icebreaker and participant data
participants_data, icebreaker_data = get_data_from_sheets()

if os.path.exists(all_groups_csv):
    with open(all_groups_csv, "r") as file:
        csvreader = csv.reader(file, delimiter=DELIMITER)
        for row in csvreader:
            opairs.add(tuple(row))

# Controleer of de juiste kolommen in Google Sheets staan
if "First name" not in participants_data.columns or "e-mail" not in participants_data.columns:
    raise ValueError("De Google Sheet moet kolommen 'First name' en 'e-mail' bevatten!")

# Maak een lijst met unieke deelnemers (op basis van e-mail)
participants = list(set(participants_data["e-mail"]))

# Maak een lijst met icebreakers
icebreakers = list(set(icebreaker_data["Icebreakers"]))

# Mogelijke groepsgroottes (kan aangepast worden)
group_sizes = [2, 3, 4, 5]

# Set om nieuwe groepen op te slaan
ngroups = set()

# Kopie van de deelnemerslijst om te bewerken
nparticipants = copy.deepcopy(participants)

# Copy of the ice breakers to edit
nicebreakers = copy.deepcopy(icebreakers)

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
    
    # Wijs een willekeurige icebreaker toe
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

# Output maken voor printen en opslaan
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
    
# Print de output
print(output_string)

# Opslaan naar een tekstbestand
with open(new_groups_txt, "w", encoding="utf8") as file:
    file.write(output_string)

# Opslaan naar een CSV-bestand
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

# Toevoegen aan historisch bestand (voorkomen van herhaalde koppelingen)
with open(all_groups_csv, "a", encoding="utf8") as file:
    for group_tuple in ngroups:
        file.write(DELIMITER.join(group_tuple[0]) + "\n")

print("\n Job Done! Nieuwe koffie groepen zijn ingedeeld.")
