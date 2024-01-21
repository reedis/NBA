import Teams
import NBA
import Player
import pandas as pd


def validateUser(userNumber):
    if userNumber == 1:
        return "samgoshen"
    elif userNumber == 2:
        return "isaacreed"
    else:
        return ""


def create_players(minutesDF):
    playerList = []
    for index, row in minutesDF.iterrows():
        playerList.append(Player.Player(row['Player'], index, row['Minutes'], row['Pace']))
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


def create_teams(playerList):
    playerList = sorted(playerList, key=lambda player: player.team)
    teamsLists = []
    teamList = []
    teamName = playerList[0].team
    for player in playerList:
        if player.team == teamName:
            teamList.append(player)
        else:
            teamName = player.team
            teamsLists.append(teamList)
            teamList = [player]
    teamList.append(playerList[-1:][0])
    teamsLists.append(teamList)
    teams = []
    for team in teamsLists:
        teams.append(Teams.Team(team, team[0].team))

    return teams


def addPercentages(playerlist, percetageList):
    playerCounter = 0
    for player in playerlist:
        for index, row in percetageList.iterrows():
            if index == player.name:
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
    season = NBA.NBA(teamsList, schedule)

    # Injuries
    injuriesCSV = '/Users/{}/Downloads/nba-injury-report.csv'.format(user)
    injuryList = pd.read_csv(injuriesCSV)
    injuryList.drop(inplace=True, labels=["Pos", "Est. Return", "Injury"], axis=1)
    injuryList.set_index("Player", inplace=True)
    qList, oList = cleanInjuryList(injuryList)

    # Applies the injuries to every team
    season.apply_injuried(qList, oList)

    return season


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


def cleanInjuryList(injuryList):
    questionablePlayers = []
    outPlayers = []
    injuryList['Team'] = injuryList['Team'].apply(lambda name: teamNamesConversionDict[name])
    qList = injuryList[injuryList['Status'] == 'Game Time Decision']
    outList = injuryList[injuryList['Status'] != 'Game Time Decision']
    for playerName, player in qList.iterrows():
        questionablePlayers.append(Player.InjuredPlayer(playerName, player['Team'], player['Status']))

    for playerName, player in outList.iterrows():
        outPlayers.append(Player.InjuredPlayer(playerName, player['Team'], player['Status']))

    return questionablePlayers, outPlayers


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
