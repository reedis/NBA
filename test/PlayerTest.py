from TestUtil import generate_random_good_player
import unittest


class TestPlayers(unittest.TestCase):

    def test_player_generation(self):
        ## sf-25%, pf-50%, c-25%
        posList = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
        player = generate_random_good_player(posList)
        print("Name: {}".format(player.name))
        print("Team: {}".format(player.team))
        print("Mins: {}".format(player.totalMins))
        print("Pace: {}".format(player.pace))
        print("Positions: {}".format(player.positions))
        print("dpm: {}".format(player.dpm))
        print("odpm: {}".format(player.odpm))
        print("ddpm: {}".format(player.ddpm))


