""" Module to calculate Norse Calendar dates. """
import datetime
import logging
from dataclasses import dataclass
from typing import List, Optional
import urllib3
import certifi

# Initialize HTTP Pool Manager
http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

class Holiday():
    """ Class containing definition of 'Holiday' object."""
    def __init__(self,
                 name: str, start_date: datetime.datetime,
                 end_date: Optional[datetime.datetime]=None,
                 desc: Optional[str]=None,
                 schedule: Optional[str]=None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = desc
        self.schedule = schedule

    def __str__(self) -> str:
        """ Method to export holiday class contents. """
        value = f"Name: {self.name}\n"
        if self.start_date is None:
            logging.error("Date Missing!")
            value += "Date: Missing\n"
        elif self.end_date is None:
            value += f"Date: {self.start_date.strftime('%m-%d-%Y')}\n"
        else:
            value += f"Start Date: {self.start_date.strftime('%m-%d-%Y')}\n"
            value += f"End Date: {self.end_date.strftime('%m-%d-%Y')}\n"
        if self.description is not None:
            value += f"Description: {self.description}\n"
        if self.schedule is not None:
            value += f"Schedule: {self.schedule}\n"
        return value

@dataclass
class MoonPhase:
    """ Class defining moon phase. """
    phase: str
    date: datetime.datetime

def get_core_dates(year: int) -> dict:
    """ Get Core Dates from API. """
    logging.info("Retrieving Core Dates for year %d", year)
    phenom_api = f"https://aa.usno.navy.mil/api/seasons?year={year}&tz=-6&dst=true"
    phenoms = http.request("GET", phenom_api)
    phenoms_json = phenoms.json()
    logging.info("Core Dates Retrieved for year %d", year)
    return phenoms_json

def get_moon_phases(year: int) -> List[MoonPhase]:
    """ Get Moon Phases from API. """
    logging.info("Retrieving Moon Phases for year %d", year)
    moon_api = f"https://aa.usno.navy.mil/api/moon/phases/date?date={year}-01-01&nump=99"
    moons = http.request("GET", moon_api)
    moons_json = moons.json()
    all_moons = []
    for moon in range(moons_json['numphases']):
        phase = moons_json['phasedata'][moon]['phase']
        date = datetime.datetime(
            moons_json['phasedata'][moon]['year'],
            moons_json['phasedata'][moon]['month'],
            moons_json['phasedata'][moon]['day'])
        all_moons.append(MoonPhase(phase=phase,date=date))
    logging.info("Moon Phases Retrieved for year %d", year)
    return all_moons

def calculate_dates(year: int) -> List[Holiday]:
    """ Calculate Holiday dates and return array of class Holiday. """
    holidays = [None] * 26  # Preallocate list for 26 holidays
    logging.info("Calculating holidays for year %d", year)
    phenoms_json = get_core_dates(year)
    phenoms_prev_json = get_core_dates(year - 1)

    # Create Holiday objects for equinoxes and solstices
    if len(phenoms_json['data']) < 6:
        logging.error("Insufficient data from phenom API for year %d.", year)
        return None

    holidays[0] = Holiday(
        "Spring Equinox",
        datetime.datetime(phenoms_json['data'][1]['year'],
                          phenoms_json['data'][1]['month'],
                          phenoms_json['data'][1]['day']))
    holidays[1] = Holiday(
        "Summer Solstice",
        datetime.datetime(phenoms_json['data'][2]['year'],
                          phenoms_json['data'][2]['month'],
                          phenoms_json['data'][2]['day']))
    holidays[2] = Holiday(
        "Fall Equinox",
        datetime.datetime(phenoms_json['data'][4]['year'],
                          phenoms_json['data'][4]['month'],
                          phenoms_json['data'][4]['day']))
    holidays[3] = Holiday(
        "Winter Solstice",
        datetime.datetime(phenoms_json['data'][5]['year'],
                          phenoms_json['data'][5]['month'],
                          phenoms_json['data'][5]['day']))

    # Get Moon Phases
    all_moons = get_moon_phases(year)

    def next_new_moon(input_date: datetime.datetime) -> Optional[datetime.datetime]:
        """ Get Next New Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "New Moon":
                return moon_counter.date
        return None

    def next_full_moon(input_date: datetime.datetime) -> Optional[datetime.datetime]:
        """ Get Next Full Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date
        return None

    def previous_full_moon(input_date: datetime.datetime) -> Optional[datetime.datetime]:
        """ Get Previous Full Moon Date."""
        for moon_counter in reversed(all_moons):
            if moon_counter.date < input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date
        return None

    def closest_full_moon(input_date: datetime.datetime) -> Optional[datetime.datetime]:
        """ Get Closest Full Moon Date. """
        days_before = input_date - previous_full_moon(input_date)
        days_after = next_full_moon(input_date) - input_date
        if days_before < days_after:
            return previous_full_moon(input_date)
        else:
            return next_full_moon(input_date)

    def previous_thursday(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Previous Thursday Date. """
        while input_date.weekday() != 3:
            input_date -= datetime.timedelta(days=1)
        return input_date

    # Calculate Holidays
    holidays[4] = Holiday(
        "Yule",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date + datetime.timedelta(days=12),
        None,
        "Start: Winter Solstice, End: 12 days after the Winter Solstice."
    )
    holidays[5] = Holiday(
        "Thorrablot",
        next_full_moon(next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date)),
        None,
        None,
        "The full moon after the new moon following the Winter Solstice."
    )
    holidays[6] = Holiday(
        "Disting",
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date),
        None,
        None,
        "The full moon after the Thorrablot."
    )
    holidays[7] = Holiday(
        "Mid-Winter",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date,
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date),
        None,
        "Start: Thorrablot, End: Next New Moon"
    )
    holidays[8] = Holiday(
        "Lenzen",
        previous_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        None,
        "Start: Full moon before the Spring Equinox, End: Full moon after the Spring Equinox"
    )
    holidays[9] = Holiday(
        "Offering to Freya",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date,
        None,
        None,
        "The Spring Equinox"
    )
    holidays[10] = Holiday(
        "Ostara",
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        None,
        None,
        "The full moon after the Spring Equinox."
    )
    holidays[11] = Holiday(
        "Sigrblot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Ostara')
        ].start_date),
        None,
        None,
        "The new moon after Ostara."
    )
    holidays[12] = Holiday(
        "Summer Nights Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Ostara')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Sigrblot')
        ].start_date,
        None,
        "Start: Ostara, End: Sigrblot"
    )
    holidays[13] = Holiday(
        "Mid-Summer",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Summer Solstice')
        ].start_date,
        None,
        None,
        "The Summer Solstice"
    )
    holidays[14] = Holiday(
        "Lammas",
        closest_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Fall Equinox')
        ].start_date),
        None,
        None,
        "The full moon closest to the Fall Equinox."
    )
    holidays[15] = Holiday(
        "Hausblot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Lammas')
        ].start_date),
        None,
        None,
        "The new moon after Lammas."
    )
    holidays[16] = Holiday(
        "Harvest Home Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Lammas')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Hausblot')
        ].start_date,
        None,
        "Start: Lammas, End: Hausblot"
    )
    holidays[17] = Holiday(
        "Alfablot",
        next_full_moon(next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Fall Equinox')
        ].start_date)),
        None,
        None,
        "The two full moons after the Fall Equinox."
    )
    holidays[18] = Holiday(
        "Disablot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Alfablot')
        ].start_date),
        None,
        None,
        "The new moon after the Alfablot."
    )
    holidays[19] = Holiday(
        "Winters Nights Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Alfablot')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Disablot')
        ].start_date,
        None,
        "Start: Alfablot, End: Disablot"
    )

    holidays[20] = Holiday(
        "Welcome Goi and Freya",
        #feb 1st
        datetime.datetime(year, 2, 1),
        None,
        None,
        "February 1st"
    )

    holidays[21] = Holiday(
        "Loki Day",
        #April 1st
        datetime.datetime(year, 4, 1),
        None,
        None,
        "April 1st"
    )

    holidays[22] = Holiday(
        "Lokabrenna",
        #July 13th
        datetime.datetime(year, 7, 13),
        None,
        None,
        "July 13th"
    )

    holidays[23] = Holiday(
        "Walpurgisnacht",
        #April 30th
        datetime.datetime(year, 4, 30),
        None,
        None,
        "April 30th"
    )

    holidays[24] = Holiday(
        "Mayday",
        #May 1st
        datetime.datetime(year, 5, 1),
        None,
        None,
        "May 1st"
    )

    previous_winter_solstice = datetime.datetime(phenoms_prev_json['data'][5]['year'],
                          phenoms_prev_json['data'][5]['month'],
                          phenoms_prev_json['data'][5]['day'])

    holidays[25] = Holiday(
        "Charming of the Plough",
        #Halfway between Winter Solstice and Spring Equinox
        (previous_winter_solstice + (((holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date) - previous_winter_solstice) / 2)),
        None,
        None,
        "Halfway between previous Winter Solstice and Spring Equinox"
    )

    # Add Sunwait holidays
    for each in range(6):
        sunwait = Holiday(
            "Sunwait",
            previous_thursday(holidays[
                next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
            ].start_date) - datetime.timedelta(days=each*7),
            None,
            None,
            "Start: 6th Thursday before Winter Solstice, End: Thursday before Winter Solstice"
        )
        holidays.append(sunwait)

    # Sort holidays by start date
    holidays = sorted(holidays, key=lambda holiday: holiday.start_date)
    return holidays
