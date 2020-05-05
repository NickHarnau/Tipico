import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re


class match_object:
    def __init__(self, home_team, away_team, quote_home_team, quote_draw, quote_away_team, event_id,
                 percentage_bet_home, percentage_bet_draw, percentage_bet_away, date, start_time):
        self.home_team = home_team
        self.away_team = away_team
        self.quote_home_team = quote_home_team
        self.quote_draw = quote_draw
        self.quote_away_team = quote_away_team
        self.percentage_bet_home = percentage_bet_home
        self.percentage_bet_draw = percentage_bet_draw
        self.percentage_bet_away = percentage_bet_away
        self.event_id = event_id
        self.date = date
        self.start_time = start_time

    def returning(self):
        print(self.home_team, " vs. ", self.away_team)
        print("Event-ID: ", self.event_id)
        print("Quotes: ", self.quote_home_team, "x", self.quote_draw, "x", self.quote_away_team)
        print("Verteilung: ", self.percentage_bet_home, "x", self.percentage_bet_draw, "x", self.percentage_bet_away)
        print("Game starts ", self.date, " ", self.start_time)
        print()


def clean_html_tag(name):
    try:
        # Entferne alle HTMLS Tags
        cleaner = re.compile('<.*?>')
        cleaned_name = re.sub(cleaner, '', name.text)
        # Entfernt alle Umbrüche und Breaks
        result_name = cleaned_name.replace('\n', '').replace('\r', '').replace('\t', '')
    except Exception as e:
        print(e)
    else:
        return result_name


def get_highlight_matches():
    url = "https://www.tipico.de/de/online-sportwetten/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.prettify()

    div_last_minute = soup.find_all("div", attrs={"e:url": '/highlights/lastminute'})

    teams = []
    quotes = []
    dates = []
    start_times = []
    matches = []
    for div in div_last_minute:

        # get Teams
        div_teams = div.find_all("div", attrs={"class": "t_cell w_113 left"})
        for team in div_teams:
            teams.append(clean_html_tag(team))

        # get Game Date
        div_date = div.find_all("meta", attrs={"itemprop": "startDate"})
        for x in div_date:
            date = x['content'][:10]
            start_time = x['content'][11:16]
            dates.append(date)
            start_times.append(start_time)

        # get Quotes
        regex = re.compile('qbut qbut*')
        div_quotes = div.find_all("div", attrs={"class": regex})

        for quote in div_quotes:
            quotes.append(clean_html_tag(quote))


        # get event ID
        div_event_id = str(div.find_all("div", attrs={"class": "e_active t_row jq-event-row-cont"}))
        lines = div_event_id.splitlines()
        result_list = []
        event_ids = []

        for line in lines:
            if "e:onupdate=" in line:
                result_list.append(line)

        for res in result_list:
            js_call = res.split("eBet.eventRow.update")[1]
            js_call_id = js_call.split(",")[1]
            js_call_result = js_call_id.split(")")[0]
            event_ids.append(js_call_result)

        # Create Match Object
        i = j = k = 0

        while i < len(teams):
            for event_id in event_ids:

                # get User-Bets
                request_url = 'https://www.tipico.de/spring/update?_=/program/eventstakeratio%253FeventId%253D{}' \
                    .format(event_id)
                r = requests.post(request_url)
                js_request_html = r.text
                html_result_list = js_request_html.split("width: ")
                numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                percent_of_bet = []
                for element in html_result_list:
                    if element[0] in numbers:
                        percent_of_bet.append(element.split(";")[0])

                # Wenn keine Daten für User Bets vorhanden
                if len(percent_of_bet) == 0:
                    obj = match_object(teams[i], teams[i + 1], quotes[j], quotes[j + 1], quotes[j + 2], event_ids[k],
                                       "N.A.", "N.A.", "N.A.", dates[k], start_times[k])
                else:
                    obj = match_object(teams[i], teams[i + 1], quotes[j], quotes[j + 1], quotes[j + 2], event_ids[k],
                                       percent_of_bet[0], percent_of_bet[1], percent_of_bet[2], dates[k],
                                       start_times[k])

                matches.append(obj)
                k += 1
                i += 2
                j += 3
    return matches


def update_row(current_match):
    import csv
    with open('CSV-Files/tipico data.csv', 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        read = list(reader)
        for row in read:
            if any(row):# Delete empty rows
                if row[1].strip() == current_match.date.strip() and row[3].strip() == current_match.home_team.strip() \
                        and row[4].strip() == current_match.away_team.strip():

                    row_id = int(row[0])

                    current_csv_data = [row[5], row[6], row[7], row[8], row[9], row[10]]
                    current_tipico_data = [current_match.quote_home_team, current_match.quote_draw,
                                           current_match.quote_away_team, current_match.percentage_bet_home,
                                           current_match.percentage_bet_draw, current_match.percentage_bet_away]

                    # compare CSV Date with extracted Data from tipico
                    if current_csv_data == current_tipico_data:
                        break
                    else:
                        list_of_elements = list(read)

                        list_of_elements[row_id][5] = current_match.quote_home_team
                        list_of_elements[row_id][6] = current_match.quote_draw
                        list_of_elements[row_id][7] = current_match.quote_away_team
                        list_of_elements[row_id][8] = current_match.percentage_bet_home
                        list_of_elements[row_id][9] = current_match.percentage_bet_draw
                        list_of_elements[row_id][10] = current_match.percentage_bet_away
                        list_of_elements[row_id][11] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

                        writer = csv.writer(open('CSV-Files/tipico data.csv', mode='w', newline=''))
                        writer.writerows(list_of_elements)
                        print("Row ", row_id, " updated")


def get_lenght():
    with open('CSV-Files/tipico data.csv') as csv_file:
        reader = csv.reader(csv_file)
        reader_list = list(reader)
        return len(reader_list)


def check_match_exists(current_match):
    with open('CSV-Files/tipico data.csv', 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            if row[1].strip() == current_match.date.strip() and row[3].strip() == current_match.home_team.strip() \
                    and row[4].strip() == current_match.away_team.strip():
                return True
        return False


def write_match_to_csv(current_match):
    # test
    try:
        if os.path.isfile('CSV-Files/tipico data.csv'):
            file_exists = True
        else:
            file_exists = False

        with open('CSV-Files/tipico data.csv', mode='a', newline='') as csv_file:
            fieldnames = ['ID', 'Date', 'Time', 'Home Team', 'Away Team', 'Home Rate', 'Draw Rate', 'Away Rate',
                          'User Bet Home', 'User Bet Draw', 'User Bet Away', 'Input Date']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")

            if not file_exists:
                writer.writeheader()
                print("Header hinzugefügt")

            match_exists = check_match_exists(current_match)

            if match_exists:
                if current_match.percentage_bet_home != "N.A." or current_match.percentage_bet_draw != "N.A." or \
                        current_match.percentage_bet_away != "N.A.":
                    update_row(current_match)

            else:
                match_id = get_lenght()

                if match_id == 0:  # keine Zeile in csv-File
                    match_id = 1

                current_date_stemp = datetime.now()
                now = current_date_stemp.strftime("%m/%d/%Y, %H:%M:%S")
                writer.writerow({'ID': match_id,
                                 'Date': current_match.date,
                                 'Time': current_match.start_time,
                                 'Home Team': current_match.home_team,
                                 'Away Team': current_match.away_team,
                                 'Home Rate': current_match.quote_home_team,
                                 'Draw Rate': current_match.quote_draw,
                                 'Away Rate': current_match.quote_away_team,
                                 'User Bet Home': current_match.percentage_bet_home,
                                 'User Bet Draw': current_match.percentage_bet_draw,
                                 'User Bet Away': current_match.percentage_bet_away,
                                 'Input Date': now})
                return True
            return False

    except Exception as error:
        print(error)


list_of_matches = get_highlight_matches()
added_matches = 0
if len(list_of_matches) == 0:
    print("Scraping-Error")
else:
    print("Found ", len(list_of_matches), " Matches")
    for match in list_of_matches:
        result = write_match_to_csv(match)
        if result:
            added_matches += 1
    print("--> Es wurden ", added_matches, " Spiele hinzugefügt")
