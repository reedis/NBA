from src.Player import *
from Utils import similar, generateMinutesByPercent


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
        self.totalPlayerMinutes = 0
        self.activeRoster = playersList
        self.playerList = playersList
        self.outList = []
        self.questionableList = []
        self.odpm = 0
        self.ddpm = 0
        self.dpm = 0
        self.playerCount = 0
        self.populate_roster(playersList)

    def populate_roster(self, playerList):
        for player in playerList:
            self.playerCount += 1
            self.dpm += player.dpm * player.timeWeight
            self.odpm += player.odpm * player.timeWeight
            self.ddpm += player.ddpm * player.timeWeight
            for position in player.positions:
                self.totalPlayerMinutes += player.positions[position]
                for pos in self.roster.keys():
                    if pos.name == position.name:
                        self.roster[pos].append(player)

        assert self.totalPlayerMinutes <= 240, "Team minutes must be less than 240, team minutes: {}".format(self.totalPlayerMinutes)

    def avgOdpm(self):
        return self.odpm / self.playerCount

    def avgDdpm(self):
        return self.ddpm / self.playerCount

    def avgDpm(self):
        return self.dpm / self.playerCount

    def sum_active_minutes(self):
        minutesSum = 0
        for player in self.activeRoster:
            minutesSum += player.totalMins
        return minutesSum

    def sum_questionable_player_min(self):
        minutesSum = 0
        for player in self.questionableList:
            minutesSum += player.totalMins
        return minutesSum

    def sum_out_player_min(self):
        minutesSum = 0
        for player in self.outList:
            minutesSum += player.totalMins
        return minutesSum

    def sort_roster(self):
        for position in self.roster:
            self.roster[position] = sorted(self.roster[position], key=lambda player: player.positions[position],
                                           reverse=True)

    def get_player(self, playerName):
        for position in self.roster:
            for player in self.roster[position]:
                if similar(player.name, playerName) >= 0.9:
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
            self.outList.append(outPlayer)
            self.odpm -= outPlayer.odpm * outPlayer.timeWeight
            self.ddpm -= outPlayer.ddpm * outPlayer.timeWeight
            self.dpm -= outPlayer.dpm * outPlayer.timeWeight
            playerInjuryMin = 0
            for position in outPlayer.positions:
                if outPlayer.positions[position] != 0:
                    for pos in minsDict.keys():
                        if pos.name == position.name:
                            minsDict[pos] += outPlayer.positions[position]
                            playerInjuryMin += outPlayer.positions[position]
                            self.outMin += outPlayer.positions[position]
                            outPlayer.positions[position] = 0
                        break

            for position in self.roster:
                for player in self.roster[position]:
                    if outPlayer.name == player.name:
                        self.roster[position].remove(player)

            for player in self.activeRoster:
                if player.name == outPlayer.name:
                    self.activeRoster.remove(player)

            self.injuryMinutes[outPlayer.name] = playerInjuryMin

        ## Players who are questionable time's is halved and distributed
        for injuredPlayer in qList:
            questionablePlayer = self.get_player(injuredPlayer.name)
            if questionablePlayer is None:
                continue
            self.questionableList.append(questionablePlayer)
            self.odpm -= (questionablePlayer.odpm * questionablePlayer.timeWeight) / 2
            self.ddpm -= (questionablePlayer.ddpm * questionablePlayer.timeWeight) / 2
            self.dpm -= (questionablePlayer.dpm * questionablePlayer.timeWeight) / 2
            playerInjuryMin = 0
            editedPlayer = questionablePlayer
            for position in questionablePlayer.positions:
                if questionablePlayer.positions[position] != 0:
                    for pos in minsDict.keys():
                        if pos.name == position.name:
                            minsDict[pos] += (questionablePlayer.positions[position] / 2)
                            playerInjuryMin += (questionablePlayer.positions[position] / 2)
                            self.questionableMin += (questionablePlayer.positions[position] / 2)
                            editedPlayer.positions[position] = (questionablePlayer.positions[position] / 2)

            for position in self.roster:
                for player in self.roster[position]:
                    if questionablePlayer.name == player:
                        self.roster[position].remove(player)
                        self.roster[position].append(editedPlayer)

            for player in self.activeRoster:
                if player.name == questionablePlayer.name:
                    self.activeRoster.remove(player)

            self.injuryMinutes[questionablePlayer.name] = playerInjuryMin

        self.distributeMinutes(minsDict)
        self.set_player_teams()
        self.smooth_team_minutes()

    def set_player_teams(self):
        for player in self.playerList:
            player.set_team(self)

    def remove_player(self, playerName):
        for position in self.roster:
            for player in self.roster[position]:
                if player.name == playerName:
                    self.roster[position].pop(player)
                    break

        for player in self.playerList:
            if player.name == playerName:
                self.playerList.remove(player)
                return

    def add_player(self, player):
        self.populate_roster([player])
        self.playerList.append(player)


    # distributes minutes taken by injury to each affected position
    def distributeMinutes(self, minutesDict):
        updatedPlayerList = []
        for position in self.roster:
            minutesToAdd = minutesDict[position]
            while minutesToAdd > 1:
                for player in self.roster[position]:
                    if player.totalMins < 30:
                        minDiff = 30 - player.totalMins
                        if minDiff >= minutesToAdd:
                            minDiff = minutesToAdd
                        for pos in player.positions.keys():
                            if pos.name == position.name:
                                player.positions[pos] += minDiff
                                player.totalMins += minDiff
                                minutesToAdd -= minDiff
                                updatedPlayerList.append(player)

                break
        for player in updatedPlayerList:
            self.update_player(player)

    def update_injury(self, player):
        self.remove_player(player.name)
        self.sumInjuryMinutes -= self.injuryMinutes[player.name]
        self.injuryMinutes[player.name] = 0
        self.add_player(player)

    def print_player_minutes(self):
        for player in self.playerList:
            player.print_player()
        print('========================')

    # Smooths a team minutes to be 240
    def smooth_team_minutes(self):
        updatedPlayerList = []
        teamMinutesOver = 240 - self.totalPlayerMinutes
        while teamMinutesOver >= 1:
            for player in self.activeRoster:
                percentageList, sumMinutes = generateMinutesByPercent(teamMinutesOver, player.totalMins,
                                                                      player.playerPositionPercentage)
                # Only add to players who have minutes to spare
                if (sumMinutes + player.totalMins) < 40 and sumMinutes > 0:
                    updatedPlayerList.append(
                        player.populate_positions(
                            pgMin=percentageList[0],
                            sgMin=percentageList[1],
                            sfMin=percentageList[2],
                            pfMin=percentageList[3],
                            cMin=percentageList[4],
                            playerPercentList=[]
                        )
                    )
                    teamMinutesOver -= sumMinutes
        for player in updatedPlayerList:
            self.update_player(player)

        self.fix_total_player_minutes()
        return self

    # Recalculates a teams total minutes
    def fix_total_player_minutes(self):
        minutesSum = 0
        for player in self.activeRoster:
            minutesSum += player.totalMins

        self.totalPlayerMinutes = minutesSum.__floor__()
        assert self.totalPlayerMinutes <= 240


    # updates a player in all places for a team
    def update_player(self, player):
        index = 0
        for oldPlayer in self.activeRoster:
            if oldPlayer.name == player.name:
                self.activeRoster[index] = player
            index += 1
        index = 0
        for pos in self.roster.keys():
            for playerOld in self.roster[pos]:
                if playerOld.name == player.name:
                    self.roster[pos].pop(index)
                    self.roster[pos].append(player)
        return self


# Creates a list of teams with the player list populated
def create_teams(playerList):
    playerList = sorted(playerList, key=lambda p: p.team)
    teamsLists = []
    teamList = []
    teamName = playerList[0].team
    for player in playerList:
        if player.team == teamName:
            teamList.append(player)
        else:
            teamName = player.team
            teamsLists.append(teamList)
            teamList = [player]
    teamList.append(playerList[-1:][0])
    teamsLists.append(teamList)
    teams = []
    for team in teamsLists:
        teams.append(Team(team, team[0].team))

    return teams
