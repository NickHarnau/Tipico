from data_download import *
from analyse import *
import seaborn as sns


seasons = ["1415", "1516", "1617", "1718", "1819", "1920"]
shortcut_dict = {"england": "E0", "scotland": "SC0", "germany": "D1", "italy": "I1", "espana": "SP1", "france": "F1",
                 "netherlands": "N1", "belgium": "B1", "portugal": "P1", "turkey": "T1", "greece": "G1"}
countries = list(shortcut_dict.keys())


# download csv. files für alle Länder
download_csv_files(shortcut_dict, countries, seasons)

# erstelle Gewinn.csv für alle Länder
country_earnings = {}
for country in countries:
    try:
        # Read Ernings
        pfad = "CSV-Files/{}/Gewinn.csv".format(country)
        country_earnings[country] = pd.read_csv(pfad)
    except FileNotFoundError as e:
        print(e)


# Merge Gewinn.csv der Länder in einen DF und rename Spalten
list_win_df = list(country_earnings.values())
Merged_df = list_win_df[0]
for df in list_win_df[1:]:
    Merged_df = Merged_df.merge(df, on="Unnamed: 0", how="left")
Merged_df.set_index("Unnamed: 0", inplace=True)
Merged_df.columns = list(countries)
max_earnings= Merged_df.copy().transpose()
Merged_df["summe"] = Merged_df.sum(axis=1)

# Heatmap
ax = sns.heatmap(max_earnings, vmin=30, linewidths=.5, xticklabels=True, cmap="YlGnBu")
ax.set_xticks(range(0,len(max_earnings.columns)))
