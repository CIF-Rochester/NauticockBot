import datetime


class Semester:
    # Season of 0 represents Spring. 1 for Fall.
    season = 0
    year = 2000

    def __init__(self, year: int, season: int) -> None:
        self.year = year
        self.season = season

    def has_passed(self) -> bool:
        c = current()
        return c.year > self.year or c.season > self.season

    def __str__(self) -> str:
        out = ""
        if self.season == 0:
            out = out + "Spring"
        else:
            out = out + "Fall"
        return out + " " + str(self.year)


def current():
    # For simplicity, I'm ignoring summer and counting the beginning of August as 'fall'
    spring = range(1, 7)
    if datetime.date.month in spring:
        return Semester(datetime.date.today().year, 0)
    else:
        return Semester(datetime.date.today().year, 1)
