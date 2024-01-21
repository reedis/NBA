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
            home = self.get_team(game['Visitor/Neutral'])
            away = self.get_team(game['Home/Neutral'])
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
