import pandas as pd
import datetime

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
    csv = '/Users/{}/Downloads/DARKO.csv'.format(user)
    seasonCSV = '/Users/{}/Downloads/sportsref_download.csv'.format(user)
    df = pd.read_csv(csv)
    df = df.set_index("Team")
    seasonList = pd.read_csv(seasonCSV)
    seasonList = seasonList.drop(["Start (ET)", "PTS", "PTS.1", "Unnamed: 6", "Unnamed: 7", "Attend.", "Arena", "Notes"], axis=1)
    seasonList.set_index("Date", inplace=True)
    teamsDict = teamCleaning(df)
    teamPairings = weeklyMatchup(seasonList)
    print(buildAnalytics(teamPairings, teamsDict))
    
def buildAnalytics(teamPairings, teamsDict):
    evaluatedDict = {}
    for home, away in teamPairings:
        evaluatedDict[(home, away)] = gameEval(teamsDict[home], teamsDict[away])
    
    evalDf = pd.DataFrame(columns=["Home", "Away", "Eval"])
    i = 0
    for key, value in evaluatedDict.items():
        evalDf.loc[i] = [str(key[0])] + [key[1]] + [value]
        i += 1
    return evalDf


def gameEval(homeTeamPoints, awayTeamPoints):
    htPowerPoints = homeTeamPoints**14.3
    atPowerPoints = awayTeamPoints**14.3
    return htPowerPoints / (htPowerPoints+atPowerPoints)

def teamCleaning(frame):
    teamsDict = {}
    teamList = frame.index
    listOfTeams = []
    for item in teamList:
        if item in teamsDict:
            next
        else:
            teamsDict[item] = 0
            listOfTeams.append(item)
    for index, row in frame.iterrows():
        teamsDict[index] += row['PTS']

    return teamsDict

def weeklyMatchup(seasonList):
    listOfMatchups = []
    for index, row in seasonList.iterrows():
        date = getFormattedTime(index)
        if (str(datetime.date.today()) == date):
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