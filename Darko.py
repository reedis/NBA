import pandas as pd
from datetime import date
import math
from Utils import validateUser, generate_season, monthToDate

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
# ***SORT BY MINUTES BEFORE DOWNLOADING*** Player Position link = https://www.basketball-reference.com/leagues/NBA_2024_play-by-play.html#pbp_stats
###########################################################

################ NAMING CONVENTIONS ######################
# Minutes (Daily Player Per-Game Projections): DARKO.csv
# Player (Current Player Skill Projections): DARKOPLAYER.csv
# Schedule: sportsref_download_CURRENTMONTH.csv -- CURRENTMONTH SHOULD BE LOWER CASE
# Injury: nba-injury-report.csv
# Position: sportsref_position.csv


alpha = 15
# this is a test push
debug = True
testing = True


def main():
    userIn = int(input("User 1 or 2: "))
    user = validateUser(userIn)
    month = input("Month: ")
    if testing:
        testDate = input("Date in format mm-dd-yyyy: ")
    else:
        testDate = ''
    season = generate_season(user, month)
    if debug:
        healthCheck(season)
    else:
        buildAnalytics(season, testDate)


def buildAnalytics(season, testDate):
    today = testDate if testing else date.today().strftime("%m-%d-%Y")
    for day in season.schedule:
        if day.strip() == today.strip():
            todayGames = season.schedule[day]
            for game in todayGames:
                homeStrength = pythagExpect(teamDDPM=game.home.ddpm, teamODPM=game.home.odpm, season=season)
                homeElo = elo(homeStrength) + 70
                awayStrength = pythagExpect(teamDDPM=game.away.ddpm, teamODPM=game.away.ddpm, season=season)
                awayElo = elo(awayStrength)
                homeWin = homeWinChance(homeElo, awayElo)
                print('{}, {}'.format(game.home.name, game.away.name))
                print('Home ({}) win % chance: {}'.format(game.home.name, homeWin * 100))
                print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(game.home.name, game.home.outMin, game.home.questionableMin))
                print("{} total team minutes: {}, total-adjusted minutes {}".format(game.home.name, game.home.totalPlayerMinutes, game.home.sum_minutes()))
                print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(game.away.name, game.away.outMin, game.away.questionableMin))
                print("{} total team minutes: {}, total-adjusted minutes {}".format(game.away.name, game.away.totalPlayerMinutes, game.away.sum_minutes()))
                print(buildROI(homeWin))
                print('----------')
    return

def healthCheck(season):
    for team in season.teams:
        print("Team: {} ODPM: {}, DDPM: {}\n Players: ".format(team.name, team.odpm, team.ddpm))
        print(" Active Roster, total active minutes: {}".format(team.sum_active_minutes()))
        for player in team.playerList:
            print("     {}: Total minutes: {}, ODPM: {}, DDPM: {},".format(player.name, player.totalMins, player.odpm, player.ddpm))
        if len(team.questionableList) != 0:
            print(" Questionable Players, total questionable minutes: {}".format(team.sum_questionable_player_min()))
            for qPlayer in team.questionableList:
                print("     {}: Total minutes: {}".format(qPlayer.name, qPlayer.totalMins))
        if len(team.outList) != 0:
            print(" Out Players, total out minutes: {}".format(team.sum_out_player_min()))
            for oPlayer in team.outList:
                print("     {}: Total minutes: {}".format(oPlayer.name, oPlayer.totalMins))
        print("Player breakdown:")
        team.print_player_minutes()

def elo(score):
    return (1504.6 - (450 * (math.log10((1 / score) - 1))))


# Projected Team win % for season -- NOT MATCHUP
def pythagExpect(teamODPM, teamDDPM, season):
    var1 = ((100 + teamODPM) - (100 + season.avgOdpm) + 100) ** 14.3
    var2 = ((100 - teamDDPM) + (100 + season.avgDdpm) - 100) ** 14.3
    return (var1 / (var1 + var2))


def homeWinChance(homeElo, awayElo):
    return (1 / ((10 ** (-(homeElo - awayElo) / 400)) + 1))


def buildROI(homeP):
    if homeP > .5:
        return (homeP * 10000) / (homeP * 100 - 100 - alpha), (alpha + (homeP * 100)) / (1 - homeP)
    else:
        return (alpha + ((1 - homeP) * 100)) / (homeP), ((1 - homeP) * 10000) / ((1 - homeP) * 100 - 100 - alpha)


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
    month = int(monthToDate(splitIndex[1][:3]))
    year = splitIndex[2]
    return str(date(int(year), int(month), int(day)))


main()
