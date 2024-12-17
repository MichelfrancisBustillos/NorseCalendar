import requests
import json
import datetime
from dataclasses import dataclass
import array

class Holiday():
    def __init__(self, name, startDate, endDate=None, desc=None):
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.description = desc
    
    def print(self):
        print("Name:", self.name)
        if self.startDate == None:
            print("Date: Missing")
        elif self.endDate == None:
            print("Date:", self.startDate.strftime('%m-%d-%Y'))
        else:
            print("Start Date:", self.startDate.strftime('%m-%d-%Y'))
            print("End Date:", self.endDate.strftime('%m-%d-%Y'))
        if self.description != None:
            print("Description:", self.description)

@dataclass
class MoonPhase():
    phase: str
    date: datetime

#Get Core Dates
lead = 6
year = (datetime.datetime.now().year) + lead
phenomAPI = "https://aa.usno.navy.mil/api/seasons?year=" + str(year) + "&tz=-6&dst=true"
phenoms = requests.get(phenomAPI, verify=False)
phenoms_json = phenoms.json()

springEquinox = Holiday("Spring Equinox", datetime.datetime(phenoms_json['data'][1]['year'], phenoms_json['data'][1]['month'], phenoms_json['data'][1]['day']))
summerSolstice = Holiday("Summar Solstice", datetime.datetime(phenoms_json['data'][2]['year'], phenoms_json['data'][2]['month'], phenoms_json['data'][2]['day']))
fallEquinox = Holiday("Fall Equinox", datetime.datetime(phenoms_json['data'][4]['year'], phenoms_json['data'][4]['month'], phenoms_json['data'][4]['day']))
winterSolstice = Holiday("Winter Solstice", datetime.datetime(phenoms_json['data'][5]['year'], phenoms_json['data'][5]['month'], phenoms_json['data'][5]['day']))

startDay = datetime.date((datetime.date.today().year + lead), 1, 1)
print("Start Day:", startDay.strftime('%m-%d-%Y'))
moonAPI = "https://aa.usno.navy.mil/api/moon/phases/date?date=" + str(startDay) + "&nump=99"
moons = requests.get(moonAPI, verify=False)
moons_json = moons.json()
allMoons = []
for moon in range(moons_json['numphases']):
    phase = moons_json['phasedata'][moon]['phase']
    date = datetime.datetime(moons_json['phasedata'][moon]['year'], moons_json['phasedata'][moon]['month'], moons_json['phasedata'][moon]['day'])
    allMoons.append(MoonPhase(phase=phase,date=date))

def nextNewMoon(date):
    for moon in allMoons:
        if moon.date > date and moon.phase == "New Moon":
            return moon.date
            break

def nextFullMoon(date):
    for moon in allMoons:
        if moon.date > date and moon.phase == "Full Moon":
            return moon.date
            break

def previousNewMoon(date):
    for moon in reversed(allMoons):
        if moon.date < date and moon.phase == "New Moon":
            return moon.date
            break

def previousFullMoon(date):
    for moon in reversed(allMoons):
        if moon.date < date and moon.phase == "Full Moon":
            return moon.date
            break

def closestFullMoon(date):
    daysBefore = date - previousFullMoon(date)
    daysAfter = nextFullMoon(date) - date
    if daysBefore < daysAfter:
        return previousFullMoon(date)
    else:
        return nextFullMoon(date)

#Calculate Holidays
yule = Holiday("Yule", winterSolstice.startDate, winterSolstice.startDate + datetime.timedelta(days=12))
thorrablot = Holiday("Thorrablot", nextFullMoon(nextNewMoon(winterSolstice.startDate)))
disting = Holiday("Disting", nextFullMoon(thorrablot.startDate))
midwinter = Holiday("Mid-Winter", thorrablot.startDate, nextNewMoon(thorrablot.startDate))
lenzen = Holiday("Lenzen", previousFullMoon(springEquinox.startDate), nextFullMoon(springEquinox.startDate))
offeringToFreya = Holiday("Offering to Freya", springEquinox.startDate)
ostara = Holiday("Ostara", nextFullMoon(springEquinox.startDate))
sigrblot = Holiday("Sigrblot", nextNewMoon(ostara.startDate))
summerTides = Holiday("Summer Nights Holy Tide", ostara.startDate, sigrblot.startDate)
midsummer = Holiday("Mid-Summer", summerSolstice.startDate)
lammas = Holiday("Lammas", closestFullMoon(fallEquinox.startDate))
hausblot = Holiday("Hausblot", nextNewMoon(lammas.startDate))
harvestTides = Holiday("Harvest Home Holy Tide", lammas.startDate, hausblot.startDate)
alfablot = Holiday("Alfablot", nextFullMoon(nextFullMoon(fallEquinox.startDate)))
disablot = Holiday("Disablot", nextNewMoon(alfablot.startDate))
wintersTides = Holiday("Winters Nights Holy Tide", alfablot.startDate, disablot.startDate)

#Output Holidays
springEquinox.print()
summerSolstice.print()
fallEquinox.print()
winterSolstice.print()
yule.print()
thorrablot.print()
disting.print()
midwinter.print()
lenzen.print()
offeringToFreya.print()
ostara.print()
sigrblot.print()
summerTides.print()
midsummer.print()
lammas.print()
hausblot.print()
harvestTides.print()
alfablot.print()
disablot.print()
wintersTides.print()
