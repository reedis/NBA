from TestUtil import generate_random_player
import unittest


class TestPlayers(unittest.TestCase):
    positionList1 = {0: 1, 1: 0, 2: 0, 3: 0, 4: 0}
    positionList12 = {0: .6, 1: .4, 2: 0, 3: 0, 4: 0}
    positionList34 = {0: 0, 1: 0, 2: .57, 3: .43, 4: 0}
    positionList345 = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
    positionList45 = {0: 0, 1: 0, 2: 0, 3: .2, 4: .8}
    psotitionList5 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1}

    def test_good_player_generation(self):
        # sf-25%, pf-50%, c-25%
        positionList345 = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
        player = generate_random_player(positionList345, 3)
        self.assertEqual(player.playerPositionPercentage[2], .25)
        self.assertEqual(player.playerPositionPercentage[3], .5)
        self.assertEqual(player.playerPositionPercentage[4], .25)
        self.assertTrue(player.totalMins > 32)
        self.assertTrue(player.ddpm >= 2)
        self.assertTrue(player.odpm >= 2)

    def test_mediocre_player_generation(self):
        positionList345 = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
        player = generate_random_player(positionList345, 3)
        self.assertEqual(player.playerPositionPercentage[2], .25)
        self.assertEqual(player.playerPositionPercentage[3], .5)
        self.assertEqual(player.playerPositionPercentage[4], .25)
        self.assertTrue(player.totalMins >= 15)
        self.assertTrue(player.ddpm >= 0)
        self.assertTrue(player.odpm >= 0)

    def test_bad_player_generation(self):
        positionList345 = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
        player = generate_random_player(positionList345, 3)
        self.assertEqual(player.playerPositionPercentage[2], .25)
        self.assertEqual(player.playerPositionPercentage[3], .5)
        self.assertEqual(player.playerPositionPercentage[4], .25)
        self.assertTrue(player.totalMins >= 0)
        self.assertTrue(player.ddpm >= -3)
        self.assertTrue(player.odpm >= -3)

    def test_player_minutes_over_40(self):
        positionList345 = {0: 0, 1: 0, 2: .25, 3: .5, 4: .25}
        player = generate_random_player(positionList345, 3)
        with self.assertRaises(AssertionError):
            player.populate_positions(20, 20, 0, 0, 0, [])
