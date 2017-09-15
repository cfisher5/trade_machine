from Trade import *
from currency import *
from click._compat import raw_input
import console_print


def make_trade(trade):
    num_teams = len(trade)
    teams = []
    for i in range(0, num_teams):
        team_name = trade[i][0]
        players_out = trade[i][1]
        players_in = trade[i][2]

        team = Team(team_name)
        team.players_out = players_out
        team.players_in = players_in

        teams.append(team)

    trade = Trade(teams)
    for t in trade.teams:
        t.calc_money_in()
        t.calc_money_out()

    decisions = []
    for t in trade.teams:
        decision, msg = trade.check_trade(t)
        decisions.append(decision)

    final_decision = trade.finalize_trade(decisions)
    print(final_decision)

def create_trade():

    team1_abbr = raw_input("Team 1: ")
    team1 = Team(team1_abbr)
    while team1.get_salary() is None:
        print("Unable to find team " + team1_abbr + ". Try again")
        team1_abbr = raw_input("Team 1: ")
        team1 = Team(team1_abbr)

    team1_players = team1.get_players()


    team2_abbr = raw_input("Team 2: ")
    team2 = Team(team2_abbr)
    while team2.get_salary() is None:
        print("Unable to find team " + team2_abbr + ". Try again")
        team2_abbr = raw_input("Team 2: ")
        team2 = Team(team2_abbr)
    team2_players = team2.get_players()

    teams = [team1, team2]
    while 1:
        ans = raw_input("Would you like to include more teams? Include them now, or type 'no' if you are done adding teams: ")
        if ans == "no":
            break
        new_team = Team(ans)
        while new_team.get_salary() is None:
            print("Unable to find team " + ans + ". Try again")
            ans = raw_input("Team: ")
            if ans == "no":
                break
            new_team = Team(ans)

        teams.append(Team(ans))

    print("")
    console_print.print_players_together(team1_players, team2_players, max(len(team1_players), len(team2_players)))
    print("----------------------------------------------------------------------------------------------------------------------------------------------")
    print("TEAM SALARY: \t\t\t\t\t" + str(currency(team1.salary)) + "\t\t|\t" + "TEAM SALARY: \t\t\t\t\t" + str(currency(team2.salary)))
    print("----------------------------------------------------------------------------------------------------------------------------------------------")

    tpes1 = team1.get_trade_exceptions()
    tpes2 = team2.get_trade_exceptions()
    console_print.print_exceptions_together(tpes1, tpes2, max(len(tpes1), len(tpes2)))
    print("")

    for i in range(2, len(teams)):
        print(teams[i].get_players())
        print("TEAM SALARY: " + currency.currency(teams[i].salary))
        if teams[i].get_trade_exceptions() != []:
            print("Trade Exceptions: ")
            print(teams[i].get_trade_exceptions())


    for i in range(0, len(teams)):
        finished = False
        while not finished:
            player_id = raw_input("Type the Player ID of a player you wish to trade from " + teams[i].name + ". Type done when you have finished: ")
            if player_id == "Done" or player_id == "done":
                finished = True
                break
            player = Player(player_id, teams[i].name)
            if player.name is not None:
                teams[i].players_out.append(player)
                if len(teams) == 2:
                    if i == 0:
                        teams[1].players_in.append(player)
                    else:
                        teams[0].players_in.append(player)
                else:
                    match = False
                    while not match:
                        destination = raw_input("What team would you like to trade " + player.name + " to? ").upper()

                        for q in range(0, len(teams)):
                            if destination == teams[q].name and destination != player.team.name:
                                match = True
                                print("You are trading " + player.name + " to " + destination)
                                teams[q].players_in.append(player)


    print("**************************************************************************************************")
    for i in range(0, len(teams)):
        print(teams[i].name + " OUT:", end=' ')
        for p in teams[i].players_out:
            print(p.name, end=', ', flush=True)

        print("")

        print(teams[i].name + " IN:", end=' ')
        for p in teams[i].players_in:
            print(p.name, end=', ', flush=True)

        print("")

    trade = Trade(teams)

    for i in teams:
        i.calc_money_in()
        i.calc_money_out()

    trade.summary()
    decisions = []
    for team in teams:
        decision, msg = trade.check_trade(team)
        print(msg)
        decisions.append(decision)
        if not decision:
            break

    print(trade.finalize_trade(decisions))


print("Welcome to the Trade Machine! To quit the program at any point, press CTRL + C")
try:
    while 1:
        response = raw_input("To begin creating a trade, type \'trade\'. To quit, type \'quit\' or press CTRL + C\n")
        if response == "trade" or response == "Trade" or response == "TRADE":
            create_trade()
        elif response == "quit" or response == "QUIT" or response == "Quit":
            break
        else:
            print("Please enter one of the two possible options.")
except(KeyboardInterrupt, EOFError) as e:
    print("\nGoodbye")
    quit(0)

