import pandas as pd
import datetime

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
##-------------------------------------------------------##

######################## LINKS ############################
# schedule link = https://www.basketball-reference.com/leagues/NBA_2024_games-november.html
# DPM/Min link = https://apanalytics.shinyapps.io/DARKO/
###########################################################

################ NAMING CONVENTIONS ######################
# Minutes (Daily Player Per-Game Projections): DARKO.csv
# Player (Current Player Skill Projections): DARKOPLAYER.csv
# Schedule: sportsref_download_CURRENTMONTH.csv -- CURRENTMONTH SHOULD BE LOWER CASE

alpha=50

seasonCSV = "sportsref_download.xls"
def validateUser(userNumber):
    if userNumber == 1:
        return sam
    elif userNumber == 2:
        return isaac
    else:
        return ""
    
isaac = "isaacreed"
sam = "samgoshen"
def main():
    userIn = int(input("User 1 or 2: "))
    user = validateUser(userIn)
    csvMinutes = '/Users/{}/Downloads/DARKO.csv'.format(user)
    csvPlayer = '/Users/{}/Downloads/DARKOPLAYER.csv'.format(user)
    seasonCSV = '/Users/{}/Downloads/sportsref_download_november.csv'.format(user)
    minutesDF = pd.read_csv(csvMinutes)
    minutesDF.drop(inplace=True, labels=["PTS", "AST","DREB","OREB","BLK","STL","TOV","FGA","FTA","FG3A","RimFGA", "PF", "date_of_projection", "Experience"], axis=1)
    minutesDF.set_index("Team", inplace=True)
    teamPlayerMinutes = minutesPerPlayer(minutesDF)
    playerDf = pd.read_csv(csvPlayer)
    playerDf = playerDf[["Team", "Player","DPM","O-DPM","D-DPM"]]
    playerDf.set_index("Team", inplace=True)
    teamPlayerDPM = dpmPerPlayer(playerDf)
    teamDPM = getTeamDPMS(teamPlayerDPM, teamPlayerMinutes)
    print(teamDPM)
    #seasonList = pd.read_csv(seasonCSV)
    #seasonList = seasonList.drop(["Start (ET)", "PTS", "PTS.1", "Unnamed: 6", "Unnamed: 7", "Attend.", "Arena", "Notes"], axis=1)
    #seasonList.set_index("Date", inplace=True)
    #teamPairings = weeklyMatchup(str(datetime.date.today()), seasonList)
    #print(buildAnalytics(teamPairings, teamsDict))
    
def buildAnalytics(teamPairings, teamsDict):
    evaluatedDict = {}
    for home, away in teamPairings:
        evaled = gameEval(teamsDict[home], teamsDict[away])
        evaluatedDict[(home, away)] = (evaled, buildROI(evaled))
    
    evalDf = pd.DataFrame(columns=["Home", "Away", "Eval", "Home ROI (HF)", "Away ROI (HF)", "Home ROI (AF)", "Away ROI (AF)"])
    i = 0
    for key, value in evaluatedDict.items():
        evalDf.loc[i] = [key[0]] + [key[1]] + [value[0]] + [value[1][0][0]] + [value[1][0][1]] + [value[1][1][0]] + [value[1][1][1]]
        i += 1
    return evalDf

def gameEval(homeTeamPoints, awayTeamPoints):
    htPowerPoints = homeTeamPoints**14.3
    atPowerPoints = awayTeamPoints**14.3
    return (htPowerPoints / (htPowerPoints+atPowerPoints))

def buildROI(homeP):
    afHomeROI = (alpha + ((1 - homeP)*100))/(homeP)
    afAwayROI = ((1-homeP)*10000)/((1-homeP)*100 - 100 - alpha)
    hfHomeROI = (homeP*10000)/(homeP*100 - 100 - alpha)
    hfAwayROI = (alpha + (homeP*100))/(1 - homeP)

    return ((hfHomeROI, hfAwayROI), (afHomeROI, afAwayROI))

def minutesPerPlayer(frame):
    teamsDict = {}
    for index, row in frame.iterrows():
        teamsDict[row['Player']] = (row['Minutes'], row['Pace'])

    return teamsDict

def dpmPerPlayer(frame):
    teamsDict = {}
    teamList = frame.index
    for item in teamList:
        if item in teamsDict:
            next
        else:
            teamsDict[item] = []
    for index, row in frame.iterrows():
        teamsDict[index].append((row['Player'],(row['DPM'], (row['O-DPM'], row['D-DPM']))))

    return teamsDict

def getTeamDPMS(dpmDict, minDict):
    teamsDict = {}
    teamList = dpmDict.keys()
    for team in teamList:
        if team not in teamsDict:
            teamsDict[team] = (0, 0)

        dpmTeam = dpmDict[team]
        for playerData in dpmTeam:
            ## takes the minutes for a player from the player-minute dictionary and divieds by total gametime for playable time weight:
            playerMinuteWeight = (minDict[playerData[0]][0]/48)
            ## ODPM is valued higher than DDPM at a 1.5:1 ratio
            ODPM = teamsDict[team][0] + ((playerData[1][1][0] * playerMinuteWeight) * 1.5)
            DDPM = teamsDict[team][1] + (playerData[1][1][1] * playerMinuteWeight)
            teamsDict[team] = (ODPM, DDPM)
    return teamsDict

def weeklyMatchup(dateToReturn, seasonList):
    listOfMatchups = []
    for index, row in seasonList.iterrows():
        date = getFormattedTime(index)
        if (dateToReturn == date):
            listOfMatchups.append((row['Home/Neutral'], row['Visitor/Neutral']))

    return listOfMatchups

            

def getFormattedTime(index):
    splitIndex = index.split(', ')
    day = splitIndex[1][4:]
    month = getNumericalMonth(splitIndex[1][:3])
    year = splitIndex[2]
    return str(datetime.date(int(year), int(month), int(day)))

def getNumericalMonth(date):
    if(date == "Jan"):
        return 1
    elif(date == "Feb"):
        return 2
    elif(date == "Mar"):
        return 3
    elif(date == "Apr"):
        return 4
    elif(date == "May"):
        return 5
    elif(date == "Jun"):
        return 6
    elif(date == "Jul"):
        return 7
    elif(date == "Aug"):
        return 8
    elif(date == "Sep"):
        return 9
    elif(date == "Oct"):
        return 10
    elif(date == "Nov"):
        return 11
    elif(date == "Dec"):
        return 12

main()
