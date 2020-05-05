import numpy as np


def favorite_win(df):
    # Create new Column "favorite_win"
    # --> True, if Favorite won
    # --> False, if Favorite lost
    df.loc[(df["difference"] > 0) & (df["FTR"] == "A"), "favorite_win"] = "True"
    df.loc[(df["difference"] < 0) & (df["FTR"] == "H"), "favorite_win"] = "True"
    df["favorite_win"].fillna("False", inplace=True)
    return df


def earning(df, new_column_name, bet_on):
    if bet_on == "favorite":
        df.loc[(df["difference"] > 0) & (df["FTR"] == "A"), new_column_name] = df["B365A"] - 1
        df.loc[(df["difference"] < 0) & (df["FTR"] == "H"), new_column_name] = df["B365H"] - 1
        df[new_column_name].fillna(-1, inplace=True)
    elif bet_on == "underdog":
        # underdog_win
        df.loc[(df["difference"] > 0) & (df["FTR"] == "H"), new_column_name] = df["B365H"] - 1
        df.loc[(df["difference"] < 0) & (df["FTR"] == "A"), new_column_name] = df["B365A"] - 1
        df[new_column_name].fillna(-1, inplace=True)
    else:
        df.loc[(df["difference"] > 0) & (df["FTR"] != "A"), new_column_name] = df["Quote 1x"] - 1
        df.loc[(df["difference"] < 0) & (df["FTR"] != "H"), new_column_name] = df["Quote x2"] - 1
        df[new_column_name].fillna(-1, inplace=True)
    return df


def calculate_doubleChance(homequote, drawquote, awayquote, df):
    # doppelte chance berechnen https://www.reddit.com/r/SoccerBetting/comments/90fd4d/how_to_calculate_double_chance/
    # Hier kann es zu Ungenauigkeiten kommen. Bei Tipico nachgerechnet - ziemlich genau """
    df["Quote 1x"] = 1 / (1 / df[homequote] + 1 / df[drawquote])
    df["Quote x2"] = 1 / (1 / df[awayquote] + 1 / df[drawquote])
    df["Quote 12"] = 1 / (1 / df[awayquote] + 1 / df[homequote])
    df["Quote 1x"] = np.where(df["Quote 1x"] < 1, 1, df["Quote 1x"])
    df["Quote x2"] = np.where(df["Quote x2"] < 1, 1, df["Quote x2"])
    df["Quote 12"] = np.where(df["Quote 12"] < 1, 1, df["Quote 12"])

    return df


def ausschuettung(data, restriction):
    if restriction == "":
        wins = {"Gewinn_Bet on Favorite": data["Gewinn 'Favorit-win'"].sum(),
                "Gewinn_Bet Double Chance": data["Gewinn 'doppelte Chance'"].sum(),
                "Gewinn_Bet on Draw": data["Gewinn 'Draw'"].sum(),
                "Gewinn_Bet on Underdog": data["Gewinn 'Underdog-win'"].sum()}
    else:
        wins = {"Gewinn_Bet on Favorite_{}".format(restriction): data["Gewinn 'Favorit-win'"].sum(),
                "Gewinn_Bet Double Chance_{}".format(restriction): data["Gewinn 'doppelte Chance'"].sum(),
                "Gewinn_Bet on Draw_{}".format(restriction): data["Gewinn 'Draw'"].sum(),
                "Gewinn_Bet on Underdog_{}".format(restriction): data["Gewinn 'Underdog-win'"].sum()}
    return wins
