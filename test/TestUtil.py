import random

from src import Player


def generate_random_good_player(posList):
    totalMin = 35 + random.randint(-2, 2)
    odpm = 4 + random.randint(-2, 2)
    ddpm = 4 + random.randint(-2, 2)
    dpm = odpm + ddpm
    player1 = Player.Player(
        "test_player",
        "TEST",
        totalMin,
        100 + random.randint(-2, 2)
    )

    playerPercentageList = [0, 0, 0, 0, 0]
    for key, value in posList.items():
        playerPercentageList[key] += value

    player1.populate_positions(
        pgMin=totalMin*playerPercentageList[0],
        sgMin=totalMin*playerPercentageList[1],
        sfMin=totalMin*playerPercentageList[2],
        pfMin=totalMin*playerPercentageList[3],
        cMin=totalMin*playerPercentageList[4],
        playerPercentList=posList.values()
    )

    player1.populate_dpms(dpm, odpm, ddpm)

    return player1





