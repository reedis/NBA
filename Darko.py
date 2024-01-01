import pandas as pd
import datetime
import math
import NBA
import Player
from Utils import validateUser, generate_season


##-------------------------------------------------------##
#                 Dictionary Structures:                  #
# Team-playerDPM Dict:                                    #
#    (Key:Value) = (TeamName: (PlayerInfo))               #
#    PlayerInfo Dict:                                     #
#        (Key:Value): = (PlayerName: (DPM, (ODPM, DDPM))) #
#                                                         #
# Player-Minute Dict:                                     #
#    (Key:Value) = (PlayerName: (Minutes, Pace))          #
#                                                         #
# Team-DPM Dict:                                          #
#    (Key:Value) = (TeamName: (ODPM, DDPM))               #
#                                                         #
# Avg-Team-DPM Dict:                                      #
#    (Key:Value) = (TeamName: (AvgODPM, AvgDDPM))         #
##-------------------------------------------------------##

######################## LINKS ############################
# schedule link = https://www.basketball-reference.com/leagues/NBA_2024_games-december.html
# DPM/Min link = https://apanalytics.shinyapps.io/DARKO/
# Injury link = https://www.rotowire.com/basketball/injury-report.php
###########################################################

################ NAMING CONVENTIONS ######################
# Minutes (Daily Player Per-Game Projections): DARKO.csv
# Player (Current Player Skill Projections): DARKOPLAYER.csv
# Schedule: sportsref_download_CURRENTMONTH.csv -- CURRENTMONTH SHOULD BE LOWER CASE
# Injury: nba-injury-report.csv
alpha = 15
# this is a test push
debug = False


def main():
    userIn = int(input("User 1 or 2: "))
    user = validateUser(userIn)
    month = input("Month: ")
    season = generate_season(user, month)
    ## todo
    minutesPerPlayer(season)
    avgODPM, avgDDPM, teamDPM = getTeamDPMs(teamPlayerDPM, teamPlayerMinutes)
    if (debug):
        print(healthCheck(avgODPM, avgDDPM, teamDPM))
    teamPairings = weeklyMatchup(str(datetime.date.today()), seasonList)
    buildAnalytics(teamPairings, avgODPM, avgDDPM, teamDPM, outMin, qMin)


def buildAnalytics(teamPairings, avgODPM, avgDDPM, teamDPM, outMin, qMin):
    evaluatedDict = {}
    for home, away in teamPairings:
        homeStrength = pythagExpect(teamDPM[home][0], teamDPM[home][1], avgODPM, avgDDPM)
        homeElo = elo(homeStrength) + 70
        awayStrength = pythagExpect(teamDPM[away][0], teamDPM[away][1], avgODPM, avgDDPM)
        awayElo = elo(awayStrength)
        homeWin = homeWinChance(homeElo, awayElo)
        print('{}, {}'.format(home, away))
        print('Home ({}) win % chance: {}'.format(home, homeWin * 100))
        print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(home, outMin[home], qMin[home]))
        print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(away, outMin[away], qMin[away]))
        print(buildROI(homeWin))
        print('----------')

    evalDf = pd.DataFrame(
        columns=["Home", "Away", "Eval", "Home ROI (HF)", "Away ROI (HF)", "Home ROI (AF)", "Away ROI (AF)"])
    i = 0
    for key, value in evaluatedDict.items():
        evalDf.loc[i] = [key[0]] + [key[1]] + [value[0]] + [value[1][0][0]] + [value[1][0][1]] + [value[1][1][0]] + [
            value[1][1][1]]
        i += 1
    return evalDf


def healthCheck(avgOdpm, avgDDpm, teams):
    sumTotal = 0
    for team in teams.keys():
        sumTotal += (pythagExpect(teams[team][0], teams[team][1], avgOdpm, avgDDpm) * 82)

    return sumTotal / 30


def elo(score):
    return (1504.6 - (450 * (math.log10((1 / score) - 1))))


# Projected Team win % for season -- NOT MATCHUP
def pythagExpect(teamODPM, teamDDPM, avgODPM, avgDDPM):
    var1 = ((100 + teamODPM) - (100 + avgDDPM) + 100) ** 14.3
    var2 = ((100 - teamDDPM) + (100 + avgODPM) - 100) ** 14.3
    return (var1 / (var1 + var2))


def homeWinChance(homeElo, awayElo):
    return (1 / ((10 ** (-(homeElo - awayElo) / 400)) + 1))


def buildROI(homeP):
    if (homeP > .5):
        return ((homeP * 10000) / (homeP * 100 - 100 - alpha), (alpha + (homeP * 100)) / (1 - homeP))
    else:
        return ((alpha + ((1 - homeP) * 100)) / (homeP), ((1 - homeP) * 10000) / ((1 - homeP) * 100 - 100 - alpha))


def minutesPerPlayer(frame, outList, questionableList):
    teamsDict = {}
    teamOUTInjuryTime = {'Atlanta Hawks': 0, 'Boston Celtics': 0, 'Brooklyn Nets': 0, 'Charlotte Hornets': 0,
                         'Chicago Bulls': 0, 'Cleveland Cavaliers': 0, 'Dallas Mavericks': 0,
                         'Denver Nuggets': 0, 'Detroit Pistons': 0, 'Golden State Warriors': 0, 'Houston Rockets': 0,
                         'Indiana Pacers': 0, 'Los Angeles Clippers': 0, 'Los Angeles Lakers': 0,
                         'Memphis Grizzlies': 0, 'Miami Heat': 0, 'Milwaukee Bucks': 0, 'Minnesota Timberwolves': 0,
                         'New Orleans Pelicans': 0, 'New York Knicks': 0,
                         'Oklahoma City Thunder': 0, 'Orlando Magic': 0, 'Philadelphia 76ers': 0, 'Phoenix Suns': 0,
                         'Portland Trail Blazers': 0, 'Sacramento Kings': 0,
                         'San Antonio Spurs': 0, 'Toronto Raptors': 0, 'Utah Jazz': 0, 'Washington Wizards': 0}
    teamQUESTIONABLEInjuryTime = {'Atlanta Hawks': 0, 'Boston Celtics': 0, 'Brooklyn Nets': 0, 'Charlotte Hornets': 0,
                                  'Chicago Bulls': 0, 'Cleveland Cavaliers': 0, 'Dallas Mavericks': 0,
                                  'Denver Nuggets': 0, 'Detroit Pistons': 0, 'Golden State Warriors': 0,
                                  'Houston Rockets': 0, 'Indiana Pacers': 0, 'Los Angeles Clippers': 0,
                                  'Los Angeles Lakers': 0,
                                  'Memphis Grizzlies': 0, 'Miami Heat': 0, 'Milwaukee Bucks': 0,
                                  'Minnesota Timberwolves': 0, 'New Orleans Pelicans': 0, 'New York Knicks': 0,
                                  'Oklahoma City Thunder': 0, 'Orlando Magic': 0, 'Philadelphia 76ers': 0,
                                  'Phoenix Suns': 0, 'Portland Trail Blazers': 0, 'Sacramento Kings': 0,
                                  'San Antonio Spurs': 0, 'Toronto Raptors': 0, 'Utah Jazz': 0, 'Washington Wizards': 0}
    for index, row in frame.iterrows():
        if row['Player'] in outList.index:
            teamsDict[row['Player']] = (0, row['Pace'])
            injuredPlayerDf = outList.loc[row['Player']]
            teamOUTInjuryTime[injuredPlayerDf['Team']] += row['Minutes']
        if row['Player'] in questionableList.index:
            teamsDict[row['Player']] = (row['Minutes'] / 2, row['Pace'])
            injuredPlayerDf = questionableList.loc[row['Player']]
            teamQUESTIONABLEInjuryTime[injuredPlayerDf['Team']] += (row['Minutes'] / 2)
        else:
            teamsDict[row['Player']] = (row['Minutes'], row['Pace'])

    return teamsDict, teamOUTInjuryTime, teamQUESTIONABLEInjuryTime


def dpmPerPlayer(frame):
    teamsDict = {}
    teamList = frame.index
    for item in teamList:
        if item in teamsDict:
            next
        else:
            teamsDict[item] = []
    for index, row in frame.iterrows():
        teamsDict[index].append((row['Player'], (row['DPM'], (row['O-DPM'], row['D-DPM']))))

    return teamsDict


def getTeamDPMs(dpmDict, minDict):
    teamsDict = {}
    teamList = dpmDict.keys()
    sumTotalDDPM = 0
    sumTotalODPM = 0
    teamsInLeauge = 30
    for team in teamList:
        if team not in teamsDict:
            teamsDict[team] = (0, 0)

        dpmTeam = dpmDict[team]
        for playerData in dpmTeam:
            ## takes the minutes for a player from the player-minute dictionary and divides by total gametime for playable time weight:
            playerMinuteWeight = (minDict[playerData[0]][0] / 48)
            ## takes in the players pace
            paceWeight = minDict[playerData[0]][1] / 100.0
            ## ODPM is valued higher than DDPM at a 1.5:1 ratio
            ODPM = teamsDict[team][0] + (playerData[1][1][0] * playerMinuteWeight * paceWeight * 0.8)
            DDPM = teamsDict[team][1] + (playerData[1][1][1] * playerMinuteWeight * paceWeight * 0.8)
            sumTotalDDPM += (playerData[1][1][1] * playerMinuteWeight * paceWeight * 0.8)
            sumTotalODPM += (playerData[1][1][0] * playerMinuteWeight * paceWeight * 0.8)
            # multiply by 0.8 to account for diminishing returns between individual player talent and on-court team talent
            teamsDict[team] = (ODPM, DDPM)

    return (sumTotalODPM / teamsInLeauge), (sumTotalDDPM / teamsInLeauge), teamsDict


def weeklyMatchup(dateToReturn, seasonList):
    listOfMatchups = []
    for index, row in seasonList.iterrows():
        date = getFormattedTime(index)
        if dateToReturn == date:
            listOfMatchups.append((row['Home/Neutral'], row['Visitor/Neutral']))
    return listOfMatchups


def getFormattedTime(index):
    splitIndex = index.split(', ')
    day = splitIndex[1][4:]
    month = getNumericalMonth(splitIndex[1][:3])
    year = splitIndex[2]
    return str(datetime.date(int(year), int(month), int(day)))


def getNumericalMonth(date):
    if (date == "Jan"):
        return 1
    elif (date == "Feb"):
        return 2
    elif (date == "Mar"):
        return 3
    elif (date == "Apr"):
        return 4
    elif (date == "May"):
        return 5
    elif (date == "Jun"):
        return 6
    elif (date == "Jul"):
        return 7
    elif (date == "Aug"):
        return 8
    elif (date == "Sep"):
        return 9
    elif (date == "Oct"):
        return 10
    elif (date == "Nov"):
        return 11
    elif (date == "Dec"):
        return 12


main()
