import pandas as pd
import os


def download_csv_files(shortcut_dict, countries, seasons):
    for country in countries:
        print(country)
        # wenn Ordner für Land noch nicht existiert
        if not os.path.exists("CSV-Files/{}".format(country)):
            os.mkdir("CSV-Files/{}".format(country))
            print("Ordner erstellt")
        for season in seasons:
            # wenn CSV File für Saison noch nicht existiert
            if not os.path.exists("CSV-Files/{}/{}.csv".format(country, season)):
                link = "https://www.football-data.co.uk/mmz4281/{}/{}.csv".format(season, shortcut_dict[country])
                print(link)
                try:
                    df = pd.read_csv(link)
                    df.to_csv("CSV-Files/{}/{}.csv".format(country, season))
                except Exception as e:
                    print(e)
