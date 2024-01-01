import pandas as pd
import datetime
import math

import Player

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

teamNamesConversionDict = {'ATL': 'Atlanta Hawks', 'BKN': 'Brooklyn Nets', 'BOS': 'Boston Celtics',
                           'CLE': 'Cleveland Cavaliers', 'CHA': 'Charlotte Hornets',
                           'CHI': 'Chicago Bulls', 'PHI': 'Philadelphia 76ers', 'MIA': 'Miami Heat',
                           'ORL': 'Orlando Magic', 'NYK': 'New York Knicks', 'TOR': 'Toronto Raptors',
                           'WAS': 'Washington Wizards', 'DET': 'Detroit Pistons', 'NOP': 'New Orleans Pelicans',
                           'MIN': 'Minnesota Timberwolves', 'DEN': 'Denver Nuggets',
                           'OKC': 'Oklahoma City Thunder', 'LAC': 'Los Angeles Clippers', 'LAL': 'Los Angeles Lakers',
                           'SAC': 'Sacramento Kings', 'DAL': 'Dallas Mavericks',
                           'HOU': 'Houston Rockets', 'PHX': 'Phoenix Suns', 'GSW': 'Golden State Warriors',
                           'UTA': 'Utah Jazz', 'POR': 'Portland Trail Blazers', 'SAS': 'San Antonio Spurs',
                           'IND': 'Indiana Pacers', 'MEM': 'Memphis Grizzlies', 'MIL': 'Milwaukee Bucks'}


def validateUser(userNumber):
    if userNumber == 1:
        return "samgoshen"
    elif userNumber == 2:
        return "isaacreed"
    else:
        return ""


def getFiles(user, month):
    # Player minutes and pace
    csvMinutes = '/Users/{}/Downloads/DARKO.csv'.format(user)
    minutesDF = pd.read_csv(csvMinutes)
    minutesDF.drop(inplace=True,
                   labels=["PTS", "AST", "DREB", "OREB", "BLK", "STL", "TOV", "FGA", "FTA", "FG3A", "RimFGA", "PF",
                           "date_of_projection", "Experience"], axis=1)
    minutesDF.set_index("Team", inplace=True)
    # Player Darko evals
    csvPlayer = '/Users/{}/Downloads/DARKOPLAYER.csv'.format(user)
    playerDf = pd.read_csv(csvPlayer)
    playerDf = playerDf[["Team", "Player", "DPM", "O-DPM", "D-DPM"]]
    playerDf.set_index("Team", inplace=True)
    # season Schedule
    seasonCSV = '/Users/{}/Downloads/sportsref_download_{}.csv'.format(user, month.lower())
    seasonList = pd.read_csv(seasonCSV)
    seasonList = seasonList.drop(
        ["Start (ET)", "PTS", "PTS.1", "Unnamed: 6", "Unnamed: 7", "Attend.", "Arena", "Notes"], axis=1)
    seasonList.set_index("Date", inplace=True)
    # Injurues
    injuriesCSV = '/Users/{}/Downloads/nba-injury-report.csv'.format(user)
    injuryList = pd.read_csv(injuriesCSV)
    injuryList.drop(inplace=True, labels=["Pos", "Est. Return", "Injury"], axis=1)
    injuryList.set_index("Player", inplace=True)
    qList, oList = cleanInjuryList(injuryList)
    return minutesDF, playerDf, seasonList, oList, qList


def cleanInjuryList(injuryList):
    questionablePlayers = []
    outPlayers = []
    injuryList['Team'] = injuryList['Team'].apply(lambda name: teamNamesConversionDict[name])
    qList = injuryList[injuryList['Status'] == 'Game Time Decision']
    outList = injuryList[injuryList['Status'] != 'Game Time Decision']
    for index, player in qList.iterrows():
        questionablePlayers.append(Player.InjuredPlayer(player['Name'], player['Team'], player['Status']))

    for index, player in outList.iterrows():
        outPlayers.append(Player.InjuredPlayer(player['Name'], player['Team'], player['Status']))

    return questionablePlayers, outPlayers

# this is a test push

debug = False


def main():
    userIn = int(input("User 1 or 2: "))
    user = validateUser(userIn)
    month = input("Month: ")
    minutesDF, playerDF, seasonList, oList, qList = getFiles(user, month)
    teamPlayerMinutes, outMin, qMin = minutesPerPlayer(minutesDF, oList, qList)
    teamPlayerDPM = dpmPerPlayer(playerDF)
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
