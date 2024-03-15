import pandas as pd
from src.Player import create_players, add_dpms, addPercentages
from src.Teams import create_teams, cleanInjuryList
from Utils import cleanedPos


class NBA:
    def __init__(self, teams, schedule):
        self.teams = teams
        self.schedule = self.generate_schedule(schedule)
        self.players = []
        self.populate_players(teams)
        self.avgOdpm = 0
        self.avgDdpm = 0
        self.teamCount = 30
        self.populatedpms()

    def generate_schedule(self, schedule):
        gamesByDate = {}
        for index, game in schedule.iterrows():
            date = makeDate(index)
            away = self.get_team(game['Visitor/Neutral'])
            home = self.get_team(game['Home/Neutral'])
            newGame = Game(date, home, away)
            if date not in gamesByDate:
                gamesByDate[date] = [newGame]
            else:
                gamesByDate[date].append(newGame)
        return gamesByDate

    def get_team(self, teamName):
        for team in self.teams:
            if team.name == teamName:
                return team

    def apply_injuried(self, outList, qList):
        for team in self.teams:
            team.apply_injuries(outList, qList)

    def populate_players(self, teams):
        for team in teams:
            for player in team.playerList:
                self.players.append(player)

    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
        else:
            raise Exception("Invalid player name of: {}".format(name))

    def populatedpms(self):
        odpms = 0
        ddpms = 0
        for team in self.teams:
            odpms += team.odpm
            ddpms += team.ddpm

        self.avgDdpm = ddpms / self.teamCount
        self.avgOdpm = odpms / self.teamCount


class Game:
    def __init__(self, date, home, away):
        self.home = home
        self.away = away
        self.date = date


def makeDate(dateString):
    weekday, monthday, year = dateString.split(', ')
    month, day = monthday.split(' ')
    monthDate = monthToDate[month]
    return monthDate + '-' + checkDay(day) + '-' + year


def checkDay(day):
    if len(day) == 1:
        return "0" + day
    return day


monthToDate = {"Jan": '01', "Feb": '02', "Mar": '03', "Apr": '04',
               "May": '05', "Jun": '06', "Jul": '07', "Aug": '08',
               "Sep": '09', "Oct": '10', "Nov": '11', "Dec": '12'}


def generate_season(user, month):
    # Player minutes and pace
    csvMinutes = '/Users/{}/Downloads/DARKO.csv'.format(user)
    minutesDF = pd.read_csv(csvMinutes)
    minutesDF.drop(inplace=True,
                   labels=["PTS", "AST", "DREB", "OREB", "BLK", "STL", "TOV", "FGA", "FTA", "FG3A", "RimFGA", "PF",
                           "date_of_projection", "Experience"], axis=1)
    minutesDF.set_index("Team", inplace=True)
    playerList = create_players(minutesDF)

    # Player Darko evals
    csvPlayer = '/Users/{}/Downloads/DARKOPLAYER.csv'.format(user)
    playerDf = pd.read_csv(csvPlayer)
    playerDf = playerDf[["Team", "Player", "DPM", "O-DPM", "D-DPM"]]
    playerDf.set_index("Player", inplace=True)
    playerList = add_dpms(playerDf, playerList)
    # Need player percentage breakdown
    positionPercentage = '/Users/{}/Downloads/sportsref_positions.csv'.format(user)
    positionsDf = pd.read_csv(positionPercentage, header=[1], index_col=[1])
    positionsDf = positionsDf[['Tm', 'PG%', 'SG%', 'SF%', 'PF%', 'C%']].fillna('0')
    percentageDf = cleanedPos(positionsDf)
    playerList = addPercentages(playerList, percentageDf)
    teamsList = create_teams(playerList)
    # season Schedule -- only one month atm can be expanded
    seasonCSV = '/Users/{}/Downloads/sportsref_download_{}.csv'.format(user, month.lower())
    schedule = pd.read_csv(seasonCSV)
    schedule = schedule.drop(
        ["Start (ET)", "PTS", "PTS.1", "Unnamed: 6", "Unnamed: 7", "Attend.", "Arena", "Notes"], axis=1)
    schedule.set_index("Date", inplace=True)

    # Builds the "season" with the teams list and schedule
    season = NBA(teamsList, schedule)

    # Injuries
    injuriesCSV = '/Users/{}/Downloads/nba-injury-report.csv'.format(user)
    injuryList = pd.read_csv(injuriesCSV)
    injuryList.drop(inplace=True, labels=["Pos", "Est. Return", "Injury"], axis=1)
    injuryList.set_index("Player", inplace=True)
    qList, oList = cleanInjuryList(injuryList)

    # Applies the injuries to every team
    season.apply_injuried(qList, oList)

    return season
