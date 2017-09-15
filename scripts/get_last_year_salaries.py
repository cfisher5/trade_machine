from urllib.request import urlopen
from bs4 import BeautifulSoup
import team_dict

last_year_file = open('spotrac_data/last_year_salaries.csv', 'w')
last_year_file.write('Player,Spotrac_ID,Team,Salary\n')

for abr, full_name in team_dict.teams.items():

    print(full_name)
    url = "http://www.spotrac.com/nba/" + full_name + "/cap/2016/"
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    active_players = soup.find('table', {'class': 'datatable'}).find('tbody').findAll('tr')

    for player in active_players:

        cols = player.findAll('td')

        name_col = cols[0]
        name = name_col.a.string
        spotrac_id = name_col.a['href']
        cap_figure = cols[8].string
        if cap_figure is None:
            cap_figure = ""

        cap_figure = cap_figure.replace(',', '')
        cap_figure = cap_figure.replace('$', '').replace(' ', '')

        last_year_file.write(name + "," + spotrac_id + "," + abr + "," + cap_figure + "\n")

last_year_file.close()
