import csv
import re
from datetime import datetime
import pandas as pd
import os

new_player_file = open('spotrac_data/roster_players_trans_temp.csv', 'w')
writer = csv.writer(new_player_file, delimiter=",")
header = ["Player","Spotrac_ID","Team","Salary","Signed_Using","Trade_Kicker","Can_Block","How_Acquired","Date_Acquired","Traded_From"]
writer.writerow(header)

signed_string = re.compile("Signed.*")
traded_string = re.compile("Traded to.*")
agreed_string = re.compile("Agreed.*")
waiver_string = re.compile("Claimed.*")

with open('spotrac_data/roster_players.csv', 'r') as players_file:

    players = csv.reader(players_file, delimiter=',')
    next(players, None)
    for player in players:

        spotrac_ID = player[1]
        team = player[2]
        match = False

        with open('spotrac_data/transactions.csv', 'r') as trans_file:

            transactions = csv.reader(trans_file, delimiter=",")
            next(transactions, None)
            player_trans = []

            for trans in transactions:

                trans_spo_ID = trans[2]
                trans_team = trans[3]
                trans_date = trans[4]
                content = trans[5]

                if spotrac_ID == trans_spo_ID and team == trans_team:

                    match = True

                    if signed_string.match(content):
                        player_trans.append((trans_date, "signed", ""))
                    if traded_string.match(content):
                        traded_from = re.findall(r'\(.*?\)', content)[1]
                        traded_from = traded_from.replace("(", "").replace(")", "")
                        if traded_from == "UTH":
                            traded_from = "UTA"
                        player_trans.append((trans_date, "traded", traded_from))
                    if agreed_string.match(content):
                        player_trans.append((trans_date, "signed", ""))
                    if waiver_string.match(content):
                        player_trans.append((trans_date, "claimed", ""))

            if player_trans != []:
                trans_to_add = player_trans[0]
                date = trans_to_add[0]
                date_to_add = datetime.strptime(date, "%b %d %Y")
                date = datetime.strftime(date_to_add, "%Y-%m-%d")

        if player_trans != []:
            player.append(trans_to_add[1])
            player.append(date)
            player.append(trans_to_add[2])
            writer.writerow(player)
        else:
            empty = ""
            player.append(empty)
            player.append(empty)
            player.append(empty)
            writer.writerow(player)

new_player_file.close()
df = pd.read_csv('spotrac_data/roster_players_trans_temp.csv', index_col=0)
df.to_csv('spotrac_data/roster_players_trans.csv')
os.remove('spotrac_data/roster_players_trans_temp.csv')





