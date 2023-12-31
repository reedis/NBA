from Player import Player
from Player import Positions
class Team:
    def __init__(self, playersList):
        self.roster = {Positions.PointGaurd: [],
                       Positions.ShootingGaurd: [],
                       Positions.SmallForward: [],
                       Positions.PowerForward: [],
                       Positions.Center: []}
        self.populate_roster(playersList)

    def populate_roster(self, playerList):
        for player in playerList:
            for position in player.positions:
                self.roster[position].append(player)

        for position in self.roster:
            self.roster[position] = sorted(self.roster[position], key=lambda player: player.positions[position], reverse=True)
