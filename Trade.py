from currency import currency
from Objects import *
import CBA

class Trade:

    def __init__(self, teams):
        self.num_teams = len(teams)
        self.teams = teams


    # PUT MOST RESTRICTIVE CHECKS FIRST
    def check_trade(self, team):

        team_msg = ''
        # Check for possible player restrictions
        for player in team.players_out:
            if player.restriction is not None and player.restriction != "Recently Traded For":
                team_msg = player.restriction_msg
                return False, team_msg
            if player.restriction == "Recently Traded For" and len(team.players_out) > 1:
                team_msg = player.restriction_msg
                return False, team_msg


        for player in team.players_in:
            # Check if any player is minimum salary
            if player.contract_type == "Minimum":
                team.money_in = team.money_in - player.salary
            # Check if player is being reacquired
            if player.old_team == team.name:
                # player was traded during season
                if player.date_acquired > CBA.season_start and player.date_acquired < CBA.season_end:
                    if date.today() < (CBA.season_start + timedelta(365)):
                        team_msg = team.name + " cannot reacquire " + player.name + " until the start of next season"
                        return False, team_msg
                # player was traded during off-season
                if player.date_acquired > CBA.season_end:
                    if date.today() < (CBA.season_end + timedelta(365)):
                        team_msg = team.name + " cannot reacquire " + player.name + " until the end of next season"
                        return False, team_msg

        # Team IS UNDER CAP + $100,000 after doing trade
        if team.salary - team.money_out + team.money_in < CBA.cap + 100000:
            pass

        # Check for possible TPE if picks/cash/rights for player trade
        elif team.players_out == [] and len(team.players_in) == 1 and team.money_in > 0:
            tpe = TradeException(team.players_in[0].salary, team.name)
            if tpe.amount is not None:
                if team.hard_capped and team.salary + team.players_in[0].salary > CBA.apron:
                    team_msg = "This trade would result in " + team.name + " crossing the apron while hardcapped. Therefore this trade is not possible."
                    return False, team_msg
                else:
                    team_msg = team.name + " can use " + str(currency(team.money_in)) + " of their TPE to make this trade work."
            else:
                team_msg = team.name + " does not have a suitable TPE to use"
                return False, team_msg

        else:
            # Team IS TAXPAYING TEAM
            if team.is_taxpaying(team.money_out, team.money_in):
                if team.money_in > team.money_out * 1.25 + 100000:
                    team_msg = team.name + " is unable to complete this trade. Since they are a taxpaying team, they are only able to take back 125% of the salary they are sending out, plus $100,000.\n"
                    team_msg += team.name + " can only take back " + str(currency(team.money_out * 1.25 + 100000)) + " in salary"
                    return False, team_msg

            # Team1 IS NOT TAXPAYING TEAM
            else:

                # Outgoing Salary b/w 0 - 6,533,333
                if team.money_out <= 6533333:
                    if team.money_in > team.money_out * 1.75 + 100000:
                        team_msg = team.name + " is unable to complete this trade. Since they are not a taxpaying team, and they are sending out less then $6,533,333 in salary, they are only able to take back 175% of the salary they are sending out, plus $100,000.\n"
                        team_msg += team.name + " can only take back " + str(currency(team.money_out * 1.75 + 100000)) + " in salary"
                        return False, team_msg

                # Outgoing salary b/w 6,533,333 - 19.6 million
                elif team.money_out <= 19600000:
                    if team.money_in > team.money_out + 5000000:
                        team_msg = team.name + " is unable to complete this trade. Since they are not a taxpaying team and they are sending out between $6,533,333 and $19.6 in salary, they are only able to take back $5 million more than the salary they are sending out.\n"
                        team_msg += team.name + " can only take back " + str(currency(team.money_out + 5000000)) + " in salary"
                        return False, team_msg

                # outgoing salary over 19.6 million
                else:
                    if team.money_in > team.money_out * 1.25 + 100000:
                        team_msg = team.name + " is unable to complete this trade. Since they are not a taxpaying team, and they are sending out over $19.6 million in salary, they are only able to take back 125% of the salary they are sending out, plus $100,000.\n"
                        team_msg += team.name + " can only take back " + str(currency(team.money_out * 1.25 + 100000)) + " in salary"
                        return False, team_msg

        if team.hard_capped == 1:
            if team.salary - team.money_out + team.money_in > CBA.apron:
                team_msg = team.name + " is hardcapped at the apron. This trade is not possible.\n"
                team_msg += team.name + " can only take back " + str(CBA.apron - team.salary - team.money_out) + " in salary"
                return False, team_msg

        return True, team_msg

    def finalize_trade(self, decisions):
        if len(decisions) != self.num_teams:
            return "This trade is not successful."
        for i in decisions:
            if not i:
                return "This trade is not successful."
        return "This trade is successful!"

    def summary(self):

        def print_team(i):
            print("**************************************************************************************************")
            print(self.teams[i].name + " trades:")
            if self.teams[i].players_out == []:
                print("Picks/Rights/Cash")
            for player in self.teams[i].players_out:
                print(player.name + " - " + str(currency(player.salary)))
            print("Combined salary out: " + str(currency(self.teams[i].money_out)))

        for i in range(0, self.num_teams):
            print_team(i)

        print("**************************************************************************************************")
