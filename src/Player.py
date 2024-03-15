from enum import Enum
from Utils import name_check, teamNamesConversionDict


class Player:
    def __init__(self, name, team, totalMins, pace):
        self.name = name
        self.team = team
        self.totalMins = totalMins
        self.timeWeight = totalMins / 48
        self.positions = {}
        self.pace = pace
        self.dpm = None
        self.odpm = None
        self.ddpm = None
        self.playerPositionPercentage = []
        self.injury_bank = None
        self.injury_status = False

    # Populates the position dictionary for the player only with the positions they actually play minutes for
    # Also populates the injury bank, the playerPositionPercentage list, and player total minutes
    def populate_positions(self, pgMin, sgMin, sfMin, pfMin, cMin, playerPercentList):
        if pgMin != 0:
            if Positions.PointGaurd not in self.positions:
                self.positions[Positions.PointGaurd] = 0
            self.positions[Positions.PointGaurd] += pgMin
        if sgMin != 0:
            if Positions.ShootingGaurd not in self.positions:
                self.positions[Positions.ShootingGaurd] = 0
            self.positions[Positions.ShootingGaurd] += sgMin
        if sfMin != 0:
            if Positions.SmallForward not in self.positions:
                self.positions[Positions.SmallForward] = 0
            self.positions[Positions.SmallForward] += sfMin
        if pfMin != 0:
            if Positions.PowerForward not in self.positions:
                self.positions[Positions.PowerForward] = 0
            self.positions[Positions.PowerForward] += pfMin
        if cMin != 0:
            if Positions.Center not in self.positions:
                self.positions[Positions.Center] = 0
            self.positions[Positions.Center] += cMin

        self.injury_bank = self.positions
        if len(playerPercentList) > 0:
            self.playerPositionPercentage = list(playerPercentList)
        self.totalMins = self.sum_playerMinutes()
        assert self.totalMins < 40, "Player minutes cannot be greater than 40, minutes: {}".format(self.totalMins)
        return self

    # sums player minutes from the position dictionary
    def sum_playerMinutes(self):
        sumMinutes = 0
        for position in self.positions:
            sumMinutes += self.positions[position]
        return sumMinutes

    def populate_dpms(self, dpm, odpm, ddpm):
        self.dpm = dpm
        self.odpm = odpm
        self.ddpm = ddpm
        return self

    def set_team(self, team):
        self.team = team

    def update_injury(self):
        self.positions = self.injury_bank
        self.team.update_injury(self)

    def print_player(self):
        first_string = "  {}, total minutes: {}".format(self.name, self.totalMins)
        pos_string = ""
        for position in self.positions:
            temp_string = "     {}: {} mins\n".format(position.name, self.positions[position])
            pos_string += temp_string
        print(first_string)
        print(pos_string.rstrip())
        print('--------')


# creates a list of Players without their positions/times/dpms populated
def create_players(minutesDF):
    playerList = []
    for index, row in minutesDF.iterrows():
        playerList.append(Player(row['Player'], index, row['Minutes'], row['Pace']))
    return playerList


# Adds player DPM, ODPM, DDPM, to each player in the list from the DataFrame
def add_dpms(playerDf, playerList):
    for index, row in playerDf.iterrows():
        playerPosCount = 0
        for player in playerList:
            if player.name == index:
                newPlayer = player.populate_dpms(row['DPM'], row['O-DPM'], row['D-DPM'])
                playerList[playerPosCount] = newPlayer
            playerPosCount += 1
    return playerList


# calculates the minutes per position for a player and populates the positon/time dictionary and total minutes
def addPercentages(playerlist, percetageList):
    playerCounter = 0
    for player in playerlist:
        for index, row in percetageList.iterrows():
            if name_check(index, player.name):
                playerMin = player.totalMins
                playerPercentList = [row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5]]
                pgMin = row.iloc[1] * playerMin
                sgMin = row.iloc[2] * playerMin
                sfMin = row.iloc[3] * playerMin
                pfMin = row.iloc[4] * playerMin
                cMin = row.iloc[5] * playerMin
                newPlayer = player.populate_positions(pgMin, sgMin, sfMin, pfMin, cMin, playerPercentList)
                playerlist[playerCounter] = newPlayer
                continue
        playerCounter += 1

    return playerlist


class InjuredPlayer:
    def __init__(self, name, team, status):
        self.name = name
        self.team = team
        self.status = status


def cleanInjuryList(injuryList):
    questionablePlayers = []
    outPlayers = []
    injuryList['Team'] = injuryList['Team'].apply(lambda name: teamNamesConversionDict[name])
    qList = injuryList[injuryList['Status'] == 'Game Time Decision']
    outList = injuryList[injuryList['Status'] != 'Game Time Decision']
    for playerName, player in qList.iterrows():
        questionablePlayers.append(InjuredPlayer(playerName, player['Team'], player['Status']))

    for playerName, player in outList.iterrows():
        outPlayers.append(InjuredPlayer(playerName, player['Team'], player['Status']))

    return questionablePlayers, outPlayers


class Positions(Enum):
    PointGaurd = 1
    ShootingGaurd = 2
    SmallForward = 3
    PowerForward = 4
    Center = 5
