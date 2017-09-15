from urllib.request import urlopen
from bs4 import BeautifulSoup
import team_dict
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import time
import pandas as pd
import os


players_file = open('spotrac_data/roster_players_temp.csv', 'w')
exceptions_file = open('spotrac_data/exceptions_temp.csv', 'w')
team_salary_file = open('spotrac_data/team_salary_temp.csv', 'w')
transactions_file = open('spotrac_data/transactions_temp.csv', 'w')

players_file.write("Player,Spotrac_ID,Team,Salary,Signed_Using,Trade_Kicker,Can_Block\n")
exceptions_file.write("Team,Type,Amount,Amount_Remaining,Expiry_Date\n")
team_salary_file.write("Team,Salary\n")
transactions_file.write("Player,Pos,Spotrac_ID,Team,Trans_Date,Trans\n")

for abr, full_name in team_dict.teams.items():

    print(full_name)
    url = "http://www.spotrac.com/nba/" + full_name + "/cap/"
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    active_players = soup.find('table', {'class': 'datatable'}).find('tbody').findAll('tr')

    # GET ALL ACTIVE PLAYERS ON ROSTER (NOT INCLUDING 2-WAY)
    for player in active_players:

        cols = player.findAll('td')

        name_col = cols[0]
        spans = name_col.findAll('span')
        name = name_col.a.string
        spotrac_id = name_col.a['href']
        num_spans = len(spans)
        trade_kicker = ""
        can_block = ""

        if num_spans == 2:
            if spans[1].find("i", {'class': 'fa-unlock'}) is not None:
                can_block = "True"
            if spans[1].find("i", {'class': 'fa-dollar'}) is not None:
                trade_kicker = "True"
        elif num_spans >= 3:
            if spans[1].find("i", {'class': 'fa-unlock'}) is not None:
                can_block = "True"
            if spans[1].find("i", {'class': 'fa-dollar'}) is not None:
                trade_kicker = "True"
            if spans[2].find("i", {'class': 'fa-unlock'}) is not None:
                can_block = "True"
            if spans[2].find("i", {'class': 'fa-dollar'}) is not None:
                trade_kicker = "True"

        signed_using = cols[3].string
        if signed_using is None:
            signed_using = ""
        cap_figure = cols[8].string
        if cap_figure is None:
            cap_figure = ""

        cap_figure = cap_figure.replace(',', '')
        cap_figure = cap_figure.replace('$', '').replace(' ','')

        players_file.write(name + "," + spotrac_id + "," + abr + "," + cap_figure + "," + signed_using + "," + trade_kicker + "," + can_block + "\n" )

    table_headers = soup.findAll('header', {'class': 'team-header'})

    for header in table_headers:

        # GET EXCEPTIONS
        if header.h2.string == "Exceptions":

            table_rows = header.findNext('table').find('tbody').findAll('tr')
            for row in table_rows:
                cols = row.findAll('td')
                type = cols[0].string

                amount = cols[1].string
                amount = amount.replace(',', '').replace('$', '')

                amount_remaining = cols[2].string
                amount_remaining = amount_remaining.replace(',', '').replace('$', '')

                expiry = cols[4].string
                if expiry is None:
                    expiry = ""

                exceptions_file.write(abr + "," + type + "," + amount + "," + amount_remaining + "," + expiry + "\n")

        # GET TEAM SALARY AMOUNT
        sal_cap_phrase = re.compile("2017-18.*Salary\sCap\sTotals")
        if sal_cap_phrase.match(header.h2.string):
            cap = header.findNext("table").find('tbody').findAll('td', {'class': 'captotal'})[1].strong.string
            cap = cap.replace("\t", "").replace(',', '').replace('$', '')

            team_salary_file.write(abr + "," + cap + "\n")

    # GET TEAM 2017 TRANSACTIONS
    url = "http://www.spotrac.com/nba/transactions/2017/" + full_name + "/"
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    time.sleep(5)

    try:
        btn = driver.find_element_by_class_name('show-more')
    except NoSuchElementException:
        print("no button in first place")
        btn = None
    except TimeoutException:
        print("cant find button initially/timeout on first load")
        btn = None

    while btn is not None:
        btn.click()
        print("button clicked")
        time.sleep(10)
        try:
            btn = driver.find_element_by_class_name('show-more')
        except NoSuchElementException:
            print("no more buttons")
            btn = None
        except TimeoutException:
            print("timeout on >1 load")
            btn = None

    source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(source, "html.parser")
    transactions = soup.find('div', {'id': 'transactionslist'})
    for t in transactions.findAll('article'):
        date = t.span.span.string
        div = t.div
        name = div.h3.a.string
        spotrac_id = div.h3.a['href']
        trans = div.p.find(text=True, recursive=True)
        possible_children = div.p.findChildren()
        for i in possible_children:
            trans = trans + i.string

        trans = trans.replace(",", "")
        transactions_file.write(name + "," + spotrac_id + "," + abr + "," + date + "," + trans + "\n")

players_file.close()
exceptions_file.close()
team_salary_file.close()
transactions_file.close()

df = pd.read_csv('spotrac_data/roster_players_temp.csv', index_col=0)
df.to_csv('spotrac_data/roster_players.csv')
os.remove('spotrac_data/roster_players_temp.csv')

df = pd.read_csv('spotrac_data/exceptions_temp.csv', index_col=0)
df.to_csv('spotrac_data/exceptions.csv')
os.remove('spotrac_data/exceptions_temp.csv')

df = pd.read_csv('spotrac_data/team_salary_temp.csv', index_col=0)
df.to_csv('spotrac_data/team_salary.csv')
os.remove('spotrac_data/team_salary_temp.csv')

df = pd.read_csv('spotrac_data/transactions_temp.csv', index_col=0)
df.to_csv('spotrac_data/transactions.csv')
os.remove('spotrac_data/transactions_temp.csv')



















