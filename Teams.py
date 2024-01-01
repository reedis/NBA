from Player import Player
from Player import Positions


class NBA:
    def __init__(self, teams):
        self.teams = teams


class Team:
    def __init__(self, playersList, name):
        self.name = name
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

        self.sort_roster()

    def sort_roster(self):
        for position in self.roster:
            self.roster[position] = sorted(self.roster[position], key=lambda player: player.positions[position],
                                           reverse=True)

    def get_player(self, playerName):
        for position in self.roster:
            for player in self.roster[position]:
                if player.name == playerName:
                    return player

    def apply_injuries(self, outList, qList):
        minsDict = {Positions.PointGaurd: 0,
                    Positions.ShootingGaurd: 0,
                    Positions.SmallForward: 0,
                    Positions.PowerForward: 0,
                    Positions.Center: 0}

        ## Players who are out their time is taken and distributed and they are removed
        for injuredPlayer in outList:
            outPlayer = self.get_player(injuredPlayer.name)
            for position in outPlayer.positions:
                if outPlayer.positions[position] != 0:
                    minsDict[position] += outPlayer.positions[position]
                    outPlayer.positions[position] = 0

            for position in self.roster:
                for player in self.roster[position]:
                    if outPlayer.name == player.name:
                        self.roster[position].remove(player)

        ## Players who are questionable time's is halved and distributed
        for injuredPlayer in qList:
            questionablePlayer = self.get_player(injuredPlayer.name)
            editedPlayer = questionablePlayer
            for position in questionablePlayer.positions:
                if questionablePlayer.positions[position] != 0:
                    minsDict[position] += (questionablePlayer.positions[position] / 2)
                    editedPlayer.positions[position] = (questionablePlayer.positions[position] / 2)

            for position in self.roster:
                for player in self.roster[position]:
                    if questionablePlayer.name == player:
                        self.roster[position].remove(player)
                        self.roster[position].append(editedPlayer)
                        self.sort_roster()

        self.distributeMinutes(minsDict)

    def distributeMinutes(self, minutesDict):
        for position in self.roster:
            minutesToAdd = minutesDict[position]
            while minutesToAdd > 0:
                for player in self.roster[position]:
                    if player.positions[position] < 30:
                        minDiff = 30 - player.positions[position]
                        if minDiff <= minutesToAdd:
                            player.positions[position] += minDiff
                            minutesToAdd -= minDiff
                        else:
                            player.positions[position] += minutesToAdd
                            minutesToAdd = 0
                ## this is to avoid a possible infinite recursion edge case
                ##      need to follow up on what the expected behavior
                break
