from datetime import date
import math
from Utils import validateUser, monthToDate
from src.NBA import generate_season

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

## SHEET ID: 1IXsvtJ3QBEvqS16Z7SIy9PRCWEDzcNybT94R0Jf9SSo

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
## debug runs ONLY healthcheck when true
debug = False
## testing allows for custom date in Building Analytics
testing = True


def main():
    #userIn = int(input("User 1 or 2: "))
    user = validateUser(2)
    #month = input("Month: ")
    if testing:
        #testDate = input("Date in format mm-dd-yyyy: ")
        print()
    else:
        testDate = ''
    season = generate_season(user, "february")
    if debug:
        healthCheck(season)
    else:
        buildAnalytics(season, "02-22-2024")


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
                print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(game.home.name, game.home.outMin,
                                                                               game.home.questionableMin))
                print("{} total team minutes: {}, total-adjusted minutes {}".format(game.home.name,
                                                                                    game.home.totalPlayerMinutes,
                                                                                    game.home.sum_active_minutes()))
                print("{} OUT-Injury minutes: {}, Q-Injury minutes: {}".format(game.away.name, game.away.outMin,
                                                                               game.away.questionableMin))
                print("{} total team minutes: {}, total-adjusted minutes {}".format(game.away.name,
                                                                                    game.away.totalPlayerMinutes,
                                                                                    game.away.sum_active_minutes()))
                print(buildROI(homeWin))
                print('----------')
    return


def healthCheck(season):
    for team in season.teams:
        print("Team: {} ODPM: {}, DDPM: {}\n Players: ".format(team.name, team.odpm, team.ddpm))
        print(" Active Roster, total active minutes: {}".format(team.sum_active_minutes()))
        for player in team.playerList:
            print("     {}: Total minutes: {}, ODPM: {}, DDPM: {},".format(player.name, player.totalMins, player.odpm,
                                                                           player.ddpm))
        if len(team.questionableList) != 0:
            print(" Questionable Players, total questionable minutes: {}".format(team.sum_questionable_player_min()))
            for qPlayer in team.questionableList:
                print("     {}: Total minutes: {}".format(qPlayer.name, qPlayer.totalMins))
        if len(team.outList) != 0:
            print(" Out Players, total out minutes: {}".format(team.sum_out_player_min()))
            for oPlayer in team.outList:
                print("     {}: Total minutes: {}".format(oPlayer.name, oPlayer.totalMins))
        ## print("Player breakdown:")
        ## team.print_player_minutes()


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

