import random

from src import Player
from src import Teams

baseGoodPlayerTimeConstant = 35
baseGoodPlayerDPMConstant = 4
baseMediocrePlayerTimeConstant = 17
baseMediocrePlayerDPMConstant = 2
baseBadPlayerTimeConstant = 2
baseBadPlayerDPMConstant = -1


def generate_random_player(posList, playerLevel, maxTimeAvailable, playerNameMod=""):
    match playerLevel:
        case 1:
            baseTimeConstant = baseBadPlayerTimeConstant
            baseDPMConstant = baseBadPlayerDPMConstant
        case 2:
            baseTimeConstant = baseMediocrePlayerTimeConstant
            baseDPMConstant = baseMediocrePlayerDPMConstant
        case _:
            baseTimeConstant = baseGoodPlayerTimeConstant
            baseDPMConstant = baseGoodPlayerDPMConstant
    totalMin = baseTimeConstant + random.randint(-2, 2)
    if totalMin > maxTimeAvailable:
        totalMin = maxTimeAvailable
    odpm = baseDPMConstant + random.randint(-2, 2)
    ddpm = baseDPMConstant + random.randint(-2, 2)
    dpm = odpm + ddpm
    player1 = Player.Player(
        "test_player"+playerNameMod,
        "TEST",
        totalMin,
        100 + random.randint(-2, 2)
    )

    playerPercentageList = [0, 0, 0, 0, 0]
    for key, value in posList.items():
        playerPercentageList[key] += value
    player1.populate_positions(
        pgMin=totalMin * playerPercentageList[0],
        sgMin=totalMin * playerPercentageList[1],
        sfMin=totalMin * playerPercentageList[2],
        pfMin=totalMin * playerPercentageList[3],
        cMin=totalMin * playerPercentageList[4],
        playerPercentList=posList.values()
    )

    player1.populate_dpms(dpm, odpm, ddpm)

    return player1


def generate_generic_team(teamName):
    teamMinutes = 240
    total_players = 16
    goodPlayers = random.randint(1, 3)
    total_players -= goodPlayers
    mediocrePlayers = random.randint(6, 9)
    total_players -= mediocrePlayers
    badPlayers = total_players

    playerList = []
    playerIndex = 1
    for i in range(goodPlayers):
        player = generate_random_player(generate_random_pos_list(), 3, teamMinutes, str(playerIndex))
        teamMinutes -= player.totalMins
        playerList.append(player)
        playerIndex += 1
    for i in range(mediocrePlayers):
        player = generate_random_player(generate_random_pos_list(), 2, teamMinutes, str(playerIndex))
        teamMinutes -= player.totalMins
        playerList.append(player)
        playerIndex += 1
    for i in range(badPlayers):
        player = generate_random_player(generate_random_pos_list(), 1, teamMinutes, str(playerIndex))
        teamMinutes -= player.totalMins
        playerList.append(player)
        playerIndex += 1

    playerList.sort(key=lambda x: x.totalMins, reverse=True)

    return Teams.Team(playerList, teamName).smooth_team_minutes()


def generate_random_pos_list():
    randPosType = random.randint(1, 3)
    match randPosType:
        # PG/SG
        case 1:
            pgVal = random.randint(0, 100)
            sgVal = 100 - pgVal
            return {0: pgVal / 100, 1: sgVal / 100, 2: 0, 3: 0, 4: 0}
        # sf/pf/c
        case 2:
            sfVal = random.randint(0, 100)
            pfVal = random.randint(0, (100 - sfVal))
            assert (sfVal + pfVal) <= 100
            cVal = 100 - (sfVal + pfVal)
            return {0: 0, 1: 0, 2: sfVal / 100, 3: pfVal / 100, 4: cVal / 100}
        case _:
            pfVal = random.randint(0, 100)
            cVal = 100 - pfVal
            return {0: 0, 1: 0, 2: 0, 3: pfVal / 100, 4: cVal / 100}
