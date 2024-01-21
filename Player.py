from enum import Enum


class Player:
    def __init__(self, name, team, totalMins, pace):
        self.name = name
        self.team = team
        self.totalMins = totalMins
        self.positions = {Positions.PointGaurd: 0, Positions.ShootingGaurd: 0, Positions.SmallForward: 0,
                          Positions.PowerForward: 0, Positions.Center: 0}
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

    def summation_of_minutes(self):
        minSum = 0
        for position in self.positions:
            minSum += self.positions[position]

        return minSum

    def set_team(self, team):
        self.team = team

    def update_injury(self, update):
        self.positions = self.injury_bank
        self.team.update_injury(self)


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
