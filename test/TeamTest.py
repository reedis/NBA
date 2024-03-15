from TestUtil import generate_generic_team
import unittest


class TestTeams(unittest.TestCase):

    def test_team_generation(self):
        testTeam = generate_generic_team("testTeam")
        print(testTeam.totalPlayerMinutes)
        testTeam2 = testTeam.smooth_team_minutes()
        print(testTeam2.totalPlayerMinutes)

