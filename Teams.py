from Player import Player
from Player import Positions


class Team:
    def __init__(self, playersList, name):
        self.name = name
        self.roster = {Positions.PointGaurd: [],
                       Positions.ShootingGaurd: [],
                       Positions.SmallForward: [],
                       Positions.PowerForward: [],
                       Positions.Center: []}
        self.injuryMinutes = {}
        self.outMin = 0
        self.questionableMin = 0
        self.playerList = playersList
        self.odpm = 0
        self.ddpm = 0
        self.dpm = 0
        self.playerCount = 0
        self.populate_roster(playersList)

    def populate_roster(self, playerList):
        for player in playerList:
            self.playerCount += 1
            self.dpm += player.dpm
            self.odpm += player.odpm
            self.ddpm += player.ddpm
            for position in player.positions:
                self.roster[position].append(player)

    def avgOdpm(self):
        return self.odpm / self.playerCount

    def avgDdpm(self):
        return self.ddpm / self.playerCount

    def avgDpm(self):
        return self.dpm / self.playerCount

    def sum_minutes(self):
        minutesSum = 0
        for pos in self.roster:
            for player in self.roster[pos]:
                minutesSum += player.positions[pos]

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
            if outPlayer is None:
                continue
            playerInjuryMin = 0
            for position in outPlayer.positions:
                if outPlayer.positions[position] != 0:
                    minsDict[position] += outPlayer.positions[position]
                    playerInjuryMin += outPlayer.positions[position]
                    self.outMin += outPlayer.positions[position]
                    outPlayer.positions[position] = 0

            for position in self.roster:
                for player in self.roster[position]:
                    if outPlayer.name == player.name:
                        self.roster[position].remove(player)
            self.injuryMinutes[outPlayer.name] = playerInjuryMin

        ## Players who are questionable time's is halved and distributed
        for injuredPlayer in qList:
            questionablePlayer = self.get_player(injuredPlayer.name)
            if questionablePlayer is None:
                continue
            playerInjuryMin = 0
            editedPlayer = questionablePlayer
            for position in questionablePlayer.positions:
                if questionablePlayer.positions[position] != 0:
                    minsDict[position] += (questionablePlayer.positions[position] / 2)
                    playerInjuryMin += (questionablePlayer.positions[position] / 2)
                    self.questionableMin += (questionablePlayer.positions[position] / 2)
                    editedPlayer.positions[position] = (questionablePlayer.positions[position] / 2)

            for position in self.roster:
                for player in self.roster[position]:
                    if questionablePlayer.name == player:
                        self.roster[position].remove(player)
                        self.roster[position].append(editedPlayer)

            self.injuryMinutes[questionablePlayer.name] = playerInjuryMin

        self.distributeMinutes(minsDict)
        self.set_player_teams()

    def set_player_teams(self):
        for player in self.playerList:
            player.set_team(self)

    def remove_player(self, playerName):
        for position in self.roster:
            for player in self.roster[position]:
                if player.name == playerName:
                    self.roster.pop(player)
                    break

        for player in self.playerList:
            if player.name == playerName:
                self.playerList.remove(player)
                return

    def add_player(self, player):
        self.populate_roster([player])
        self.playerList.append(player)

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

    def update_injury(self, player):
        self.remove_player(player.name)
        self.sumInjuryMinutes -= self.injuryMinutes[player.name]
        self.injuryMinutes[player.name] = 0
        self.add_player(player)
