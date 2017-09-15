from Trade import *
from Objects import *


success = "This trade is successful!"
fail = "This trade is not successful."


def test_trade(i, trade, expected_decision):

    for t in trade.teams:
        t.calc_money_in()
        t.calc_money_out()

    decisions = []
    for t in trade.teams:
        decision, msg = trade.check_trade(t)
        decisions.append(decision)

    final_decision = trade.finalize_trade(decisions)

    if final_decision == expected_decision:
        print("Passed test trade" + str(i))
    else:
        print("Failed test trade" + str(i))



#TEST 1: TOR [JV, LN] - MIA [GD] = successful
tor = Team("TOR")
mia = Team("MIA")
tor.players_out = [Player(8055, "TOR"), Player(13329, "TOR")]
mia.players_out = [Player(6146, "MIA")]

tor.players_in = mia.players_out
mia.players_in = tor.players_out

trade_teams = [tor, mia]
trade = Trade(trade_teams)
test_trade(1, trade, success)

#TEST 2: TOR[KL] - BOS[AH] = not successful (lowry resign restriction *as of 2017-09-08*)
tor = Team("TOR")
bos = Team("BOS")
tor.players_out = [Player(2536, "TOR")]
bos.players_out = [Player(2199, "BOS")]

tor.players_in = bos.players_out
bos.players_in = tor.players_out

trade_teams = [tor, bos]
trade = Trade(trade_teams)
test_trade(2, trade, fail)

#TEST 3: TOR[] - DET [AB] = not successful (tor hardcap restriction)
tor = Team("TOR")
det = Team("DET")
tor.players_out = []
det.players_out = [Player(6901, "DET")]

tor.players_in = det.players_out
det.players_in = tor.players_out

trade_teams = [tor, det]
trade = Trade(trade_teams)
test_trade(3, trade, fail)

#TEST 4: CLE[KI] - PHX[EB, JJ] = successful
cle = Team("CLE")
phx = Team("PHX")
cle.players_out = [Player(8051, "CLE")]
phx.players_out = [Player(6900, "PHX"), Player(23599, "PHX")]

cle.players_in = phx.players_out
phx.players_in = cle.players_out

trade_teams = [cle, phx]
trade = Trade(trade_teams)
test_trade(4, trade, success)

#TEST 5:

