import Player
import Teams

player1 = Player.Player("player1", 30, 5, 0, 0, 0, 2)
player2 = Player.Player("player2",25, 8, 15, 8, 0, 0)
player3 = Player.Player("player3",20, 15, 5, 0, 0, 0)
player4 = Player.Player("player4",15, 0, 7, 23, 4, 0)
player5 = Player.Player("player5",10, 0, 0, 5, 30, 0)

pList1 = [player5, player4, player3, player1, player2]

team1 = Teams.Team(pList1)

for pos in team1.roster:
    print(pos)
    for player in team1.roster[pos]:
        print(player.name)
        print(player.positions[pos])
