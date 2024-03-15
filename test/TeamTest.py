from TestUtil import generate_generic_team
from src import NBA, Darko
import unittest
import pandas as pd


class TestTeams(unittest.TestCase):

    def test_team_generation(self):
        testTeam = generate_generic_team("testTeam")
        self.assertTrue(testTeam.totalPlayerMinutes <= 240)
        self.assertEqual(len(testTeam.activeRoster), 16)

    def test_simple_game(self):
        team1 = generate_generic_team("Team1")
        team2 = generate_generic_team("Team2")
        teamList = [team1, team2]
        date = 'randomWeekday, Jan 1, 2024'

        testSchedule = {
            'Date': [date],
            'Visitor/Neutral': [team1.name],
            'Home/Neutral': [team2.name]
        }
        df = pd.DataFrame(testSchedule).set_index('Date')
        nba = NBA.NBA(teamList, df)
        Darko.buildAnalytics(nba, '01-01-2024')

    def test_multi_game_day(self):
        team1 = generate_generic_team("Team1")
        team2 = generate_generic_team("Team2")
        team3 = generate_generic_team("Team3")
        team4 = generate_generic_team("Team4")
        team5 = generate_generic_team("Team5")
        team6 = generate_generic_team("Team6")
        teamList = [team1, team2, team3, team4, team5, team6]
        date = 'randomWeekday, Jan 1, 2024'

        testSchedule = {
            'Date': [date, date, date],
            'Home/Neutral': [team1.name, team3.name, team5.name],
            'Visitor/Neutral': [team2.name, team4.name, team6.name]
        }
        df = pd.DataFrame(testSchedule).set_index('Date')
        nba = NBA.NBA(teamList, df)
        Darko.buildAnalytics(nba, '01-01-2024')


    # TODO this is not good - same team should have similar %'s per call
    def test_same_team_game(self):
        team1 = generate_generic_team("Team1")
        teamList = [team1, team1]
        date = 'randomWeekday, Jan 1, 2024'

        testSchedule = {
            'Date': [date],
            'Home/Neutral': [team1.name],
            'Visitor/Neutral': [team1.name]
        }
        df = pd.DataFrame(testSchedule).set_index('Date')
        nba = NBA.NBA(teamList, df)
        Darko.buildAnalytics(nba, '01-01-2024')

