from datetime import datetime, timedelta, date
import CBA
import csv
from currency import currency


class Team:

    def __init__(self, name):
        self.name = name.upper()
        self.salary = self.get_salary()
        self.hard_capped = self.is_hardcap()
        self.players_out = []
        self.picks_out = []
        self.players_in = []
        self.picks_in = []
        self.money_out = 0
        self.money_in = 0

    def calc_money_out(self):
        money = 0
        for player in self.players_out:
            money += player.salary
        self.money_out = money

    def calc_money_in(self):
        money = 0
        for player in self.players_in:
            money += player.salary
        self.money_in = money

    def get_salary(self,):
        with open('scripts/spotrac_data/team_salary.csv', 'r') as sal_file:
            salaries = csv.reader(sal_file, delimiter=',')
            next(salaries, None)
            for sal in salaries:
                if self.name == sal[0]:
                    return int(sal[1])

    def is_taxpaying(self, money_out, money_in):
        if self.salary - money_out + money_in > CBA.tax:
            return True
        return False

    def is_hardcap(self):
        with open('scripts/spotrac_data/exceptions.csv', 'r') as ex_file:
            exceptions = csv.reader(ex_file, delimiter=',')
            next(exceptions, None)
            for ex in exceptions:
                if self.name == ex[0] and ex[1] == "Non-Taxpayer Mid-Level Exception":
                    if int(ex[3]) < CBA.non_taxpayer_MLE - CBA.taxpayer_MLE:
                        return True
                if self.name == ex[0] and ex[1] == "Bi-Annual Exception":
                    if int(ex[3]) < int(ex[2]):
                        return True
        return False

    def salary_as_currency(self):
        sal = self.salary
        return str(currency(sal))

    def money_out_as_currency(self):
        out = self.money_out
        return str(currency(out))

    def money_in_as_currency(self):
        m_in = self.money_in
        return str(currency(m_in))

    def get_players(self):

        team = []
        with open('scripts/spotrac_data/roster_players_trans.csv', 'r') as players_file:
            players = csv.reader(players_file, delimiter=',')
            next(players, None)
            for p in players:
                if p[2] == self.name:
                    new_ID = p[1].split("/")[5]
                    player = Player(new_ID, self.name)
                    team.append(player)
        return team

    def get_trade_exceptions(self):

        tpes = []
        with open('scripts/spotrac_data/exceptions.csv', 'r') as ex_file:
            exceptions = csv.reader(ex_file, delimiter=',')
            next(exceptions, None)
            for ex in exceptions:
                if self.name == ex[0] and ex[1] == "Trade Exception":

                    today = datetime.today()
                    date_str = ex[4]
                    exp_date = datetime.strptime(date_str, "%m/%d/%Y")
                    if today < exp_date:
                        tpe = (ex[4], currency(int(ex[3])))
                        tpes.append(tpe)
        return tpes

    def get_draft_picks(self):

        dps = []
        with open('scripts/spotrac_data/draft_picks.csv', 'r') as pick_file:
            picks = csv.reader(pick_file, delimiter=',')
            next(picks, None)
            for p in picks:
                if p[0] == self.name:
                    dps.append(str(p[1]) + " Pick #" + str(p[2]))
        return dps


class Player:
    def __init__(self, player_id, team):

        self.name = None
        self.ID = "http://www.spotrac.com/redirect/player/" + str(player_id) + "/"
        self.numID = player_id
        self.team = Team(team)
        self.salary = 0
        self.contract_type = None
        self.trade_kicker = False
        self.can_block = False
        self.date_acquired = None
        self.how_acquired = None
        self.old_team = None
        self.get_data(player_id, self.ID, team)
        self.restriction_msg = None
        self.restriction = self.check_restrictions()

    def get_data(self, player_id, ID, team):
        found = False
        with open('scripts/spotrac_data/roster_players_trans.csv', 'r') as players_file:
            players = csv.reader(players_file, delimiter=',')
            next(players, None)
            for p in players:
                if p[1] == ID and p[2] == team:
                    found = True
                    self.name = p[0]
                    if p[3] != '-':
                       self.salary = int(p[3])
                    self.contract_type = p[4]
                    if p[5] == "True":
                        self.trade_kicker = True
                    if p[6] == "True":
                        self.can_block = True
                    if p[7] != '':
                        self.how_acquired = p[7]
                        if self.how_acquired == "traded":
                            self.old_team = p[9]
                    if p[8] != '':
                        date_acquired_str = p[8]
                        date = datetime.strptime(date_acquired_str, "%Y-%m-%d").date()
                        self.date_acquired = date
        if not found:
            print("Unable to find player with ID=" + str(player_id) + " on " + team)

    def salary_as_currency(self):
        sal = self.salary
        return str(currency(sal))

    def check_restrictions(self):
        # Common date comparisons
        Dec15 = date(2017, 12, 15)
        Jan15 = date(2018, 1, 15)

        # Resigned with Bird rights + 20% raise and team > Cap restriction
        if (self.contract_type == "Bird" or self.contract_type == "Early Bird") and self.team.salary > CBA.cap and self.date_acquired is not None:
            with open('scripts/spotrac_data/last_year_salaries.csv', 'r') as csv_file:
                players_last_year = csv.reader(csv_file, delimiter=',')
                next(players_last_year, None)
                for p in players_last_year:
                    spotrac_ID = p[1]
                    p_team = p[2]
                    last_salary = p[3]
                    if self.ID == spotrac_ID:
                        if self.team.name.lower() == p_team.lower() and float(self.salary) > (float(last_salary) * 1.2):
                            if date.today() < max(self.date_acquired + timedelta(90), Jan15):
                                if max(self.date_acquired + timedelta(90), Jan15) == self.date_acquired + timedelta(90):
                                    self.restriction_msg = self.name + " cannot be traded because 3 months have not passed since he re-signed using Bird rights with a 20% raise in salary and " + self.team.name + " is over the cap."
                                else:
                                    self.restriction_msg = self.name + " cannot be traded until Jan 15 because he re-signed using Bird rights with a 20% raise in salary and " + self.team.name + " is over the cap."
                                return "Salary Increase"

        # Traded within last 2 months restriction
        if self.how_acquired == "traded":
            if date.today() < (self.date_acquired + timedelta(days=60)):
                self.restriction_msg = self.name + " cannot be traded with other players because 2 months have not passed since he was traded for."
                return "Recently Traded For"

        # Drafted restriction
        if self.contract_type == "Rookie" and self.date_acquired is not None:
            if date.today() < self.date_acquired + timedelta(30):
                self.restriction_msg = self.name + " cannot be traded because 30 days have not yet passed since he was signed as a rookie."
                return "Draft Pick Signing"

        # Signed within last 3 months restriction
        if self.how_acquired == "signed" and self.contract_type != "Rookie":
            if date.today() < (max(self.date_acquired + timedelta(90), Dec15)):
                if max(self.date_acquired + timedelta(90), Dec15) == self.date_acquired + timedelta(90):
                    self.restriction_msg = self.name + " cannot be traded because 3 months have not passed since he was signed."
                else:
                    self.restriction_msg = self.name + " cannot be traded until December 15."
                return "Signed Signed"

        # Claimed off waivers restriction
        if self.how_acquired == "claimed" and self.date_acquired is not None:
            # Player claimed after season started
            if self.date_acquired > CBA.season_start:
                if date.today() < self.date_acquired + timedelta(30):
                    self.restriction_msg = self.name + " was claimed off waivers during the season, meaning he cannot be traded until 30 days have passed."
                    return "Waiver Claim"
            # Player claimed during offseason
            else:
                if date.today() < CBA.season_start + timedelta(29):
                    self.restriction_msg = self.name + " was claimed off waivers during the off-season, so he cannot be traded until the 30th day of the season"
                    return "Waiver Claim"
        return None


class TradeException:
    def __init__(self, amount_needed, team):
        self.name = "TPE"
        self.expiry = None
        self.team = team
        self.amount = self.set_amount(team, amount_needed)

    def set_amount(self, team, amount_needed):
        tpes = []
        with open('scripts/spotrac_data/exceptions.csv', 'r') as ex_file:
            exceptions = csv.reader(ex_file, delimiter=',')
            next(exceptions, None)
            for ex in exceptions:
                if team == ex[0] and ex[1] == "Trade Exception":
                    tpe = (ex[4], int(ex[3]))
                    tpes.append(tpe)

            for i in tpes:
                today = datetime.today()
                date_str = i[0]

                exp_date = datetime.strptime(date_str, "%m/%d/%Y")
                if today < exp_date and int(i[1]) >= (amount_needed - 100000):
                    self.expiry = date_str
                    return amount_needed
            return None



