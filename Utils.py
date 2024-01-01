import Teams
from NBA import NBA
import Player
import pandas as pd
from itertools import groupby

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
        for player in playerList:
            if player.name == index:
                player.populate_dpms(row['DPM'], row['O-DPM'], row['D-DPM'])
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

    teams = []
    for team in teamsLists:
        teams.append(Teams.Team(team, team[0].team))

    return teams






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
    teamsList = create_teams(playerList)

    # season Schedule -- only one month atm can be expanded
    seasonCSV = '/Users/{}/Downloads/sportsref_download_{}.csv'.format(user, month.lower())
    schedule = pd.read_csv(seasonCSV)
    schedule = schedule.drop(
        ["Start (ET)", "PTS", "PTS.1", "Unnamed: 6", "Unnamed: 7", "Attend.", "Arena", "Notes"], axis=1)
    schedule.set_index("Date", inplace=True)

    # Builds the "season" with the teams list and schedule
    season = NBA([], schedule)

    # Injuries
    injuriesCSV = '/Users/{}/Downloads/nba-injury-report.csv'.format(user)
    injuryList = pd.read_csv(injuriesCSV)
    injuryList.drop(inplace=True, labels=["Pos", "Est. Return", "Injury"], axis=1)
    injuryList.set_index("Player", inplace=True)
    qList, oList = cleanInjuryList(injuryList)

    # Applies the injuries to every team
    season.apply_injuried(qList, oList)

    return season


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
