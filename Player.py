from enum import Enum
class Player:
    def __init__(self, name, pgMin, sgMin, sfMin, pfMin, cMin, pace, isInjured=False, injuryStatus=None):
        self.name = name
        self.positions = self.populate_positions_dict(pgMin, sgMin, sfMin, pfMin, cMin)
        self.pace = pace
        self.totalMin = self.summation_of_minutes()
        self.isInjured = isInjured
        self.injuryStatus = injuryStatus

    def populate_positions_dict(self, pgMin, sgMin, sfMin, pfMin, cMin):
        returnDict = {Positions.PointGaurd: 0, Positions.ShootingGaurd: 0, Positions.SmallForward: 0,
                      Positions.PowerForward: 0, Positions.Center: 0}
        if pgMin != 0:
            returnDict[Positions.PointGaurd] = pgMin
        if sgMin != 0:
            returnDict[Positions.ShootingGaurd] = sgMin
        if sfMin != 0:
            returnDict[Positions.SmallForward] = sfMin
        if pfMin != 0:
            returnDict[Positions.PowerForward] = pfMin
        if cMin != 0:
            returnDict[Positions.Center] = cMin
        return returnDict

    def summation_of_minutes(self):
        minSum = 0
        for position in self.positions:
            minSum += self.positions[position]

        return minSum


class Positions(Enum):
    PointGaurd = 1
    ShootingGaurd = 2
    SmallForward = 3
    PowerForward = 4
    Center = 5
