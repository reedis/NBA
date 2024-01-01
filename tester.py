import Player
import Teams

player1 = Player.Player("player1", "team1", 30, 5, 0, 0, 0, 2)
player2 = Player.Player("player2", "team1", 25, 8, 15, 8, 0, 0)
player3 = Player.Player("player3", "team1", 20, 15, 5, 0, 0, 0)
player4 = Player.Player("player4", "team1", 15, 0, 7, 23, 4, 0)
player5 = Player.Player("player5", "team1", 10, 0, 0, 5, 30, 0)
injuredPlayer = Player.InjuredPlayer("player1", "team1", "Out")
pList1 = [player5, player4, player3, player1, player2]
pList2 = [player1, player2]
team1 = Teams.Team(pList1, "team")
team2 = Teams.Team(pList2, "team")
for pos in team1.roster:
    print(pos)
    for player in team1.roster[pos]:
        print("{},{}".format(player.name, player.positions[pos]))
    print("________")

team1.apply_injuries([injuredPlayer], [])
print('============')

for pos in team1.roster:
    print(pos)
    for player in team1.roster[pos]:
        print("{},{}".format(player.name, player.positions[pos]))
    print("________")
