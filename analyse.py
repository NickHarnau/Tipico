import pandas as pd
from analyse_funktionen import *
import numpy as np
from os import listdir
from os.path import isfile, join


def get_earnings(country):

    # # # # # CREATING DATAFRAME --> "DATA" # # # # #

    onlyfiles = [f for f in listdir("CSV-Files/{}".format(country)) if isfile(join("CSV-Files/{}".format(country), f))]
    # opening csv-files
    files = []
    for data in onlyfiles:
        if not data == "Gewinn.csv":
            files.append(pd.read_csv("CSV-Files/{}/{}".format(country, data)))
    columns = ["Date", "HomeTeam", "AwayTeam", "FTR", "B365H", "B365D", "B365A", "Spieltag"]

    for file in files:
        file["Spieltag"] = 1
        match_days = [0, 9]
        j = 9
        i = 1
        while i < 35:
            file.loc[match_days[-2]:match_days[-1], "Spieltag"] = i
            j += 9
            i += 1
            match_days.append(j)

    together = pd.concat(files)  # alle df in einen
    data = together[columns]  # relevanten spalten wählen
    data.reset_index(inplace=True)  # neuen index generieren, alter wird zu einer spalte
    data.drop("index", axis=1, inplace=True)  # alten index eliminieren

    # Difference = Quoten-Unterschied
    # ist difference > 0 --> Away-Team ist Favorit
    # ist difference < 0 --> Home-Team ist Favorit
    data["difference"] = (data["B365H"] - data["B365A"])

    # Eliminieren der Reihen, in denen die quote zwischen A u. H exakt gleich ist --> 15 Stk
    same_quote = data.loc[data["difference"] == 0].index
    data.drop(same_quote, inplace=True)

    data = calculate_doubleChance("B365H", "B365D", "B365A", data)  # neue Spalten für Quoten Doppelte Chance
    wins = {}  # -->wins als dict für die Gewinne für alle Analysen

    # test
    #

    # # # # #   ANALYSE 1: GEWINNE BEIM WETTEN AUF FAVORIT/UNDERDOG/DRAW/DOPPELTE CHANCE # # # # #

    # Gewinnberechnung bei Wette "Favorit gewinnt"
    data = favorite_win(data)  # --> Add new Column "Favorite win" ; True or False
    data = earning(data, new_column_name="Gewinn 'Favorit-win'", bet_on="favorite")

    # Gewinnberechnung bei Wette "Doppelte Chance"
    data = earning(data, new_column_name="Gewinn 'doppelte Chance'", bet_on="double chance")

    # Gewinnberechnung bei Wette "Unentschieden"
    data["Gewinn 'Draw'"] = np.where(data["FTR"] == "D", data["B365D"] - 1, -1)

    # Gewinnberechnung bei Wette "Underdog gewinnt" --> neue Spalte
    data = earning(data, new_column_name="Gewinn 'Underdog-win'", bet_on="underdog")
    wins.update(ausschuettung(data=data, restriction=""))

    #
    #

    # # # # # ANALYSE 2: BERÜCKSICHTIGUNG VON QUOTEN-DIFFERENZEN

    # absoluten Unterschied zwiscen Home und Away ist größer als 4 / kleiner gleich 4 /  zwischen 1 und 2:
    difference_larger_4 = data.loc[data.difference.abs() > 4]
    difference_smaller_4 = data.loc[data.difference.abs() <= 4]
    difference_between_1_and_2 = data.loc[(data.difference.abs() <= 2) & (data.difference.abs() > 1)]

    restrictions = [difference_larger_4, difference_smaller_4, difference_between_1_and_2]
    difference_restrictions = ["Difference >4", "Difference <=4", "Difference 1<x<2"]

    i = 0
    while i < len(restrictions):
        wins.update(ausschuettung(restrictions[i], difference_restrictions[i]))
        i += 1

    #
    #

    # # # # # ANALYSE 3: BERÜCKSICHTIGUNG VON HOME UND AWAY

    # Select Data, where Home (Away) is Favorite
    home_is_favorite = data.loc[data["difference"] < 0]
    away_is_favorite = data.loc[data["difference"] > 0]
    favorits = [home_is_favorite, away_is_favorite]
    string_favorits = ["HomeIsFav", "AwayIsFav"]

    i = 0
    # Analyse Home und Away als Favorit
    while i < len(favorits):
        wins.update(ausschuettung(favorits[i], string_favorits[i]))
        i += 1

    # Analyse Home und Away als Favorit + Difference-Ausprägungen
    j = 0
    for fav in favorits:
        difference_larger_4 = fav.loc[fav.difference.abs() > 4]
        difference_smaller_4 = fav.loc[fav.difference.abs() <= 4]
        difference_between_1_and_2 = fav.loc[(fav.difference.abs() <= 2) & (fav.difference.abs() > 1)]
        if j == 0:
            favorit = "HomeIsFav"
        else:
            favorit = "AwayIsFav"
        restrictions = [difference_larger_4, difference_smaller_4, difference_between_1_and_2]
        difference_restrictions = [favorit + "_Difference >4", favorit + "_Difference <=4",
                                   favorit + "_Difference 1<x<2"]

        i = 0
        while i < len(restrictions):
            wins.update(ausschuettung(restrictions[i], difference_restrictions[i]))
            i += 1
        j += 1

    print(wins)
    wins_date_frame = pd.DataFrame([wins])
    wins_date_frame = wins_date_frame.transpose()
    wins_series = pd.Series(wins_date_frame[0])
    wins_series.sort_values(ascending=False)
    wins_date_frame.to_csv("CSV-Files/{}/Gewinn.csv".format(country))
