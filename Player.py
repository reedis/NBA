from enum import Enum


class Player:
    def __init__(self, name, team, totalMins, pace):
        self.name = name
        self.team = team
        self.totalMins = totalMins
        self.positions = {}
        self.pace = pace
        self.dpm = None
        self.odpm = None
        self.ddpm = None
        self.injury_bank = None
        self.injury_status = False

    def populate_positions(self, pgMin, sgMin, sfMin, pfMin, cMin):
        if pgMin != 0:
            self.positions[Positions.PointGaurd] = pgMin
        if sgMin != 0:
            self.positions[Positions.ShootingGaurd] = sgMin
        if sfMin != 0:
            self.positions[Positions.SmallForward] = sfMin
        if pfMin != 0:
            self.positions[Positions.PowerForward] = pfMin
        if cMin != 0:
            self.positions[Positions.Center] = cMin

        self.injury_bank = self.positions
        return self

    def populate_dpms(self, dpm, odpm, ddpm):
        self.dpm = dpm
        self.odpm = odpm
        self.ddpm = ddpm
        return self

    def set_team(self, team):
        self.team = team

    def update_injury(self, update):
        self.positions = self.injury_bank
        self.team.update_injury(self)

    def print_player(self):
        first_string = "  {}, total minutes: {}".format(self.name, self.totalMins)
        pos_string = ""
        for position in self.positions:
            temp_string = "     {}: {} mins\n".format(position.name, self.positions[position])
            pos_string += temp_string
        print(first_string)
        print(pos_string.rstrip())
        print('--------')

class InjuredPlayer:
    def __init__(self, name, team, status):
        self.name = name
        self.team = team
        self.status = status


class Positions(Enum):
    PointGaurd = 1
    ShootingGaurd = 2
    SmallForward = 3
    PowerForward = 4
    Center = 5
