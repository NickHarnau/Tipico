from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class match_obj:
    def __init__(self,  home_team, away_team, home_goals, away_goals, date):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.date = date


url = "https://www.flashscore.de/"
button_xpath = "/html/body/div[5]/div[1]/div/div[1]/div[2]/div[7]/div[2]/div[1]/div[2]/div[1]/div"

driver = webdriver.Firefox()
driver.get(url)

# click yesterday
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
element.click()

# Opening Games
pa = '//div[@class="event__expander icon--expander expand"]'
elements = driver.find_elements_by_xpath('//div[@class="event__expander icon--expander expand"]')
lenght = len(elements)
i = 0
for _ in elements:
    try:
        if i == lenght:
            break
        el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, pa)))
        driver.execute_script("arguments[0].click();", el)
        i += 1

    except TimeoutException as error:
        print("Error: ", error)
print("Opened all windows...")
# Find Matches
match_class = driver.find_elements_by_class_name("event__match.event__match--oneLine")
matches = []

for match in match_class:
    try:
        raw = match.get_attribute('innerHTML')
        cleantext = BeautifulSoup(raw, features="html5lib").text

        if "Beendet" in cleantext:
            res = cleantext.split("Beendet")[1]
            re = res[:-7]
            home_goals = re.split("-")[0][-2]
            away_goals = re.split("-")[1][1]
            home = re.split("-")[0][:-2]
            if "(" in home:
                home = home.split("(")[0]
            away = re.split("-")[1][2:]
            if "(" in away:
                away = away.split("(")[0]

            # to do: check if home goals and away goals to int possible -> yes: create object   no: continue

            yesterday = datetime.strftime(datetime.now() - timedelta(1), "%m.%d.%Y")
            matches.append(match_obj(home, away, home_goals, away_goals, yesterday))
    except Exception as error:
        print("Error: ", error)

for m in matches:
    print(m.home_team, " vs. ", m.away_team, ": ", m.home_goals, " - ", m.away_goals)
