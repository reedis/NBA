from difflib import SequenceMatcher


def validateUser(userNumber):
    if userNumber == 1:
        return "samgoshen"
    elif userNumber == 2:
        return "isaacreed"
    else:
        return ""


def name_check(name1, name2):
    return ((
                    (similar(name1, name2) >= .9) or
                    (similar(name1, name2) == 0.8461538461538461)
            ) and
            ((not (similar(name1, name2) == 0.9333333333333333)) or ("Den" in name1)))


def makeDate(dateString):
    weekday, monthday, year = dateString.split(', ')
    month, day = monthday.split(' ')
    monthDate = monthToDate[month]
    return monthDate + '-' + day + '-' + year


def cleanedPos(positionDf):
    posList = ['PG%', 'SG%', 'SF%', 'PF%', 'C%']
    for column in positionDf:
        if column in posList:
            col = positionDf[column]
            for idx, row in col.to_frame().iterrows():
                if type(row.iloc[0]) is str:
                    if row.iloc[0] != '0':
                        positionDf[column][idx] = (int(row.iloc[0][:-1]) / 100)
                    else:
                        positionDf[column][idx] = 0
    return positionDf


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


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

monthToDate = {"Jan": '1', "Feb": '2', "Mar": '3', "Apr": '4',
               "May": '5', "Jun": '6', "Jul": '7', "Aug": '8',
               "Sep": '9', "Oct": '10', "Nov": '11', "Dec": '12'}
