monthToDate = {"Jan": '1', "Feb": '2', "Mar": '3', "Apr": '4',
               "May": '5', "Jun": '6', "Jul": '7', "Aug": '8',
               "Sep": '9', "Oct": '10', "Nov": '11', "Dec": '12'}


def makeDate(dateString):
    weekday, monthday, year = dateString.split(', ')
    month, day = monthday.split(' ')
    monthDate = monthToDate[month]
    return monthDate + '-' + day + '-' + year


class NBA:
    def __init__(self, teams, schedule):
        self.teams = teams
        self.schedule = self.generate_schedule(schedule)

    def generate_schedule(self, schedule):
        gamesByDate = {}
        for game in schedule.iterrows():
            date = makeDate(game['Date'])
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


class Game:
    def __init__(self, home, away, date):
        self.home = home
        self.away = away
        self.date = date
