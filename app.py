from flask import Flask, request, render_template, session
from Trade import Trade
import Objects
from scripts import team_dict


app = Flask(__name__)
app.secret_key = "Nr\x97\xc7\xa9j\xa6J\xd4\x18\xd8\xfc\xe5\xa4\xb6\xe5\x87\xbdmA\x97\xf3n"


@app.route('/')
def index():
    return render_template('index.html', team_list=sorted(team_dict.teams), error_msg="")


@app.errorhandler(500)
def page_not_found(e):
    error_msg = "Something went wrong. Perhaps you tried using the web browser's 'back' " \
                "and/or 'forward' button. Please refrain from doing so. Instead, use the 'Create Trade' " \
                "and 'Edit Trade' buttons, or press the header to take you to the homepage!"
    return render_template('index.html', team_list=sorted(team_dict.teams), error_msg=error_msg)


@app.route('/trade', methods=['GET', 'POST'])
@app.route('/trade/<trade>', methods=['GET', 'POST'])
def trade(trade=None):

    trade_info = []
    if trade is not None:
        teams = []
        team_names = []
        teams_involved = trade.split('&')
        for team in teams_involved:
            if team != '':
                team_name, players = team.split(':')
                team_names.append(team_name)
                team = Objects.Team(team_name)
                teams.append(team)
                for p in players.split(','):
                    if p != "":
                        p_id, p_to = p.split('-')
                        p_out = [team_name, p_id, p_to]
                        print(p_out)
                        trade_info.append(p_out)

        teamnames = []
        print(trade_info)

    else:

        print("no trade given")
        teams = []
        team_names = []

        # print(session['teams'])
        team1_name = request.form.get('team1')
        team_names.append(team1_name)
        team1 = Objects.Team(team1_name)
        teams.append(team1)

        team2_name = request.form.get('team2')
        team_names.append(team2_name)
        team2 = Objects.Team(team2_name)
        teams.append(team2)

        team3_name = request.form.get('team3')
        if team3_name != "None":
            team3 = Objects.Team(team3_name)
            team_names.append(team3_name)
            teams.append(team3)

        team4_name = request.form.get('team4')
        if team4_name != "None":
            team4 = Objects.Team(team4_name)
            team_names.append(team4_name)
            teams.append(team4)

        session['teams'] = team_names

        teamnames = "-".join(team_names)
        print(teamnames)

        session['trade_info'] = trade_info
    return render_template('trade.html', teams=teams, team_names=team_names, trade_info=trade_info)


@app.route('/checktrade/<trade>', methods=['GET', 'POST'])
@app.route('/checktrade', methods=['GET', 'POST'])
def checktrade(trade=None):

    print(trade)

    trade_string = ""
    team_names = session['teams']
    team_dict = {}
    allteams = []

    for t in team_names:
        team_obj = Objects.Team(t)
        allteams.append(team_obj)
        team_dict[t] = team_obj

    all_players = []
    for team in team_names:
        trade_string += team + ":"
        p_out_list = request.args.getlist(team + "_players_traded")
        print(p_out_list)
        for p in p_out_list:
            t_from, p_id, t_to = p.split("-")
            trade_string += p_id + "-" + t_to + ","
            all_players.append([t_from, p_id, t_to])

        trade_string += "&"

    for player in all_players:

        t_from = player[0]
        p_id = player[1]
        t_to = player[2]

        p = Objects.Player(p_id, t_from)

        team_dict[t_from].players_out.append(p)
        team_dict[t_to].players_in.append(p)

    for i in team_dict.values():
        print(i.name)
        for p in i.players_out:
            print("out")
            print(p.name)
        for p in i.players_in:
            print("in")
            print(p.name)

    trade = Trade(allteams)

    for t in trade.teams:
        t.calc_money_in()
        t.calc_money_out()

    print("TRADE STRING:" + trade_string)

    decisions = []
    msgs = {}
    for t in trade.teams:
        decision, msg = trade.check_trade(t)
        msg = msg.split('\n')
        msgs[t] = msg
        decisions.append(decision)

    final_decision = trade.finalize_trade(decisions)

    trade_info = session['trade_info']

    return render_template('checktrade.html', trade=trade, team_names=team_names, final_decision=final_decision, msgs=msgs, trade_string=trade_string, trade_info=trade_info)
