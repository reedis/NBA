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
        self.injury_bank = None
        self.injury_status = False

    def populate_positions(self, pgMin, sgMin, sfMin, pfMin, cMin):
        if pgMin != 0:
            self.positions[Positions.PointGaurd] = pgMin
        if sgMin != 0:
            self.positions[Positions.ShootingGaurd] = sgMin
        if sfMin != 0:
            self.positions[Positions.SmallForward] = sfMin
        if pfMin != 0:
            self.positions[Positions.PowerForward] = pfMin
        if cMin != 0:
            self.positions[Positions.Center] = cMin

        self.injury_bank = self.positions
        return self

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


def create_players(minutesDF):
    playerList = []
    for index, row in minutesDF.iterrows():
        playerList.append(Player(row['Player'], index, row['Minutes'], row['Pace']))
    return playerList


def add_dpms(playerDf, playerList):
    for index, row in playerDf.iterrows():
        playerPosCount = 0
        for player in playerList:
            if player.name == index:
                newPlayer = player.populate_dpms(row['DPM'], row['O-DPM'], row['D-DPM'])
                playerList[playerPosCount] = newPlayer
            playerPosCount += 1
    return playerList


def addPercentages(playerlist, percetageList):
    playerCounter = 0
    for player in playerlist:
        for index, row in percetageList.iterrows():
            if name_check(index, player.name):
                playerMin = player.totalMins
                pgMin = row.iloc[1] * playerMin
                sgMin = row.iloc[2] * playerMin
                sfMin = row.iloc[3] * playerMin
                pfMin = row.iloc[4] * playerMin
                cMin = row.iloc[5] * playerMin
                newPlayer = player.populate_positions(pgMin, sgMin, sfMin, pfMin, cMin)
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
