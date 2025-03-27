import pandas as pd

def load_and_clean_bankruptcy_data(filepath):
    df = pd.read_csv(filepath, delimiter=";")
    df.columns = df.columns.str.strip().str.replace('"', '')
    df["PronouncedBankruptcies_1"] = df["PronouncedBankruptcies_1"].astype(str).str.strip().astype(int)
    df["Regions"] = df["Regions"].str.strip()
    return df

def load_population_all_years(filepath):
    pop_df = pd.read_csv(filepath, delimiter=";")
    pop_df.columns = pop_df.columns.str.strip().str.replace('"', '')
    
    # Filter out national total
    pop_df = pop_df[
        (pop_df["Sex"] == "Total male and female") &
        (pop_df["Regions"] != "The Netherlands")
    ].copy()

    pop_df["COROP_Name"] = pop_df["Regions"].str.replace(r"\s*\(CR\)", "", regex=True).str.strip()

    # COROP name → code mapping
    corop_name_to_code = {
        "Oost-Groningen": "CR01", "Delfzijl en omgeving": "CR02", "Overig Groningen": "CR03",
        "Noord-Friesland": "CR04", "Zuidwest-Friesland": "CR05", "Zuidoost-Friesland": "CR06",
        "Noord-Drenthe": "CR07", "Zuidoost-Drenthe": "CR08", "Zuidwest-Drenthe": "CR09",
        "Noord-Overijssel": "CR10", "Zuidwest-Overijssel": "CR11", "Twente": "CR12",
        "Veluwe": "CR13", "Achterhoek": "CR14", "Arnhem/Nijmegen": "CR15", "Zuidwest-Gelderland": "CR16",
        "Utrecht": "CR17", "Kop van Noord-Holland": "CR18", "Alkmaar en omgeving": "CR19",
        "IJmond": "CR20", "Agglomeratie Haarlem": "CR21", "Zaanstreek": "CR22",
        "Groot-Amsterdam": "CR23", "Het Gooi en Vechtstreek": "CR24",
        "Agglomeratie Leiden en Bollenstreek": "CR25", "Agglomeratie 's-Gravenhage": "CR26",
        "Delft en Westland": "CR27", "Oost-Zuid-Holland": "CR28", "Groot-Rijnmond": "CR29",
        "Zuidoost-Zuid-Holland": "CR30", "Zeeuwsch-Vlaanderen": "CR31", "Overig Zeeland": "CR32",
        "West-Noord-Brabant": "CR33", "Midden-Noord-Brabant": "CR34", "Noordoost-Noord-Brabant": "CR35",
        "Zuidoost-Noord-Brabant": "CR36", "Noord-Limburg": "CR37", "Midden-Limburg": "CR38",
        "Zuid-Limburg": "CR39", "Flevoland": "CR40"
    }

    pop_df["COROP_Code"] = pop_df["COROP_Name"].map(corop_name_to_code)
    pop_df = pop_df[["Periods", "COROP_Code", "Population on 1 January (number)"]]
    pop_df.rename(columns={"Periods": "Year", "Population on 1 January (number)": "Population"}, inplace=True)
    return pop_df

def merge_population(monthly_df, pop_df):
    monthly_df["Year"] = pd.to_datetime(monthly_df["Date"]).dt.year
    monthly_df["Regions"] = monthly_df["Regions"].str.strip().str.upper()
    pop_df["COROP_Code"] = pop_df["COROP_Code"].str.strip().str.upper()
    
    merged_df = monthly_df.merge(
        pop_df,
        left_on=["Regions", "Year"],
        right_on=["COROP_Code", "Year"],
        how="left"
    )
    
    return merged_df
