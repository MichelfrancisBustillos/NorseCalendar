""" Module to calculate Norse Calendar dates. """
# pylint: disable=line-too-long
import datetime
import logging
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
import urllib3
import certifi

# Initialize HTTP Pool Manager
http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

@dataclass
class Holiday():
    """ Class containing definition of 'Holiday' object."""   
    name: str
    start_date: datetime.datetime
    end_date: Optional[datetime.datetime]=None
    description: Optional[str]=None
    schedule: Optional[str]=None

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

def calculate_dates(year: int) -> List[Holiday] | None:
    """ Calculate Holiday dates and return array of class Holiday. """
    holidays = []
    logging.info("Calculating holidays for year %d", year)

    phenoms_json = get_core_dates(year)
    phenoms_prev_json = get_core_dates(year - 1)

    # Create Holiday objects for equinoxes and solstices
    if len(phenoms_json['data']) < 6 or len(phenoms_prev_json['data']) < 6:
        logging.error("Insufficient data from phenom API for year %d.", year)
        return None

    holidays.append(Holiday(
        "Spring Equinox",
        datetime.datetime(phenoms_json['data'][1]['year'],
                          phenoms_json['data'][1]['month'],
                          phenoms_json['data'][1]['day'])))
    holidays.append(Holiday(
        "Summer Solstice",
        datetime.datetime(phenoms_json['data'][2]['year'],
                          phenoms_json['data'][2]['month'],
                          phenoms_json['data'][2]['day'])))
    holidays.append(Holiday(
        "Fall Equinox",
        datetime.datetime(phenoms_json['data'][4]['year'],
                          phenoms_json['data'][4]['month'],
                          phenoms_json['data'][4]['day'])))
    holidays.append(Holiday(
        "Winter Solstice",
        datetime.datetime(phenoms_json['data'][5]['year'],
                          phenoms_json['data'][5]['month'],
                          phenoms_json['data'][5]['day'])))

    # Get Moon Phases
    all_moons = get_moon_phases(year)

    def next_new_moon(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Next New Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "New Moon":
                return moon_counter.date
        return datetime.datetime(0,0,0)

    def next_full_moon(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Next Full Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date
        return datetime.datetime(0,0,0)

    def previous_full_moon(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Previous Full Moon Date."""
        for moon_counter in reversed(all_moons):
            if moon_counter.date < input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date
        return datetime.datetime(0,0,0)

    def closest_full_moon(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Closest Full Moon Date. """

        days_before = input_date - previous_full_moon(input_date)
        days_after = next_full_moon(input_date) - input_date
        if days_before < days_after:
            return previous_full_moon(input_date)
        return next_full_moon(input_date)

    def previous_thursday(input_date: datetime.datetime) -> datetime.datetime:
        """ Get Previous Thursday Date. """
        while input_date.weekday() != 3:
            input_date -= datetime.timedelta(days=1)
        return input_date

    # Calculate Holidays
    holidays.append(Holiday(
        "Yule",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date + datetime.timedelta(days=12),
        "12 day celebration, each day celebrating a different God/Goddess/community/kin",
        "Start: Winter Solstice, End: 12 days after the Winter Solstice."
    ))
    holidays.append(Holiday(
        "Thorrablot",
        next_full_moon(next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
        ].start_date)),
        None,
        "Welcoming Old man winter and Thor into the home to allow them to warm up after a cold winter",
        "The full moon after the new moon following the Winter Solstice."
    ))
    holidays.append(Holiday(
        "Disting",
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date),
        None,
        "Celebration of Freya and the love in your life",
        "The full moon after the Thorrablot."
    ))
    holidays.append(Holiday(
        "Mid-Winter",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date,
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Thorrablot')
        ].start_date),
        "Marks the year's longest night and the symbolic rebirth of the sun",
        "Start: Thorrablot, End: Next New Moon"
    ))
    holidays.append(Holiday(
        "Lenzen",
        previous_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        "Comes in a perilous time in spring when food supplies that were stored for the winter were running low and new sources were not available yet, fasting during this time is used to honor those who suffered with hunger and famine",
        "Start: Full moon before the Spring Equinox, End: Full moon after the Spring Equinox"
    ))
    holidays.append(Holiday(
        "Offering to Freya",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date,
        None,
        "Celebrates Freya's gift of fertility over the land and her hand in making spring come",
        "The Spring Equinox"
    ))
    holidays.append(Holiday(
        "Ostara",
        next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date),
        None,
        "A celebration of spring, making it through the winter. Celebrating Idunn, freya, Ostara",
        "The full moon after the Spring Equinox."
    ))
    holidays.append(Holiday(
        "Sigrblot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Ostara')
        ].start_date),
        None,
        "Marks the start of campaigning season where weather was getting warmer, Offering sacrifices for victories in battle",
        "The new moon after Ostara."
    ))
    holidays.append(Holiday(
        "Summer Nights Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Ostara')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Sigrblot')
        ].start_date,
        "The spring festival that marked the beginning of the Norse year's summer season",
        "Start: Ostara, End: Sigrblot"
    ))
    holidays.append(Holiday(
        "Mid-Summer",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Summer Solstice')
        ].start_date,
        None,
        "Marks the peak power of the sun goddess Sol (Sunna), celebrating the shortest night of the year",
        "The Summer Solstice"
    ))
    holidays.append(Holiday(
        "Lammas",
        closest_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Fall Equinox')
        ].start_date),
        None,
        "Marks the start of the Harvest season (Gratitude for hard work leading to abundance)",
        "The full moon closest to the Fall Equinox."
    ))
    holidays.append(Holiday(
        "Hausblot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Lammas')
        ].start_date),
        None,
        "Celebration of giving thanks for the bountiful harvest and time to prepare for the coming winter",
        "The new moon after Lammas."
    ))
    holidays.append(Holiday(
        "Harvest Home Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Lammas')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Hausblot')
        ].start_date,
        "Marks the end of the summer season, serving as the major harvest and community celebration",
        "Start: Lammas, End: Hausblot"
    ))

    holidays.append(Holiday(
        "Alfablot",
        next_full_moon(next_full_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Fall Equinox')
        ].start_date)),
        None,
        "Remembering the fallen male ancestors and offerings to honor the protective spirits of the land",
        "The two full moons after the Fall Equinox."
    ))

    holidays.append(Holiday(
        "Disablot",
        next_new_moon(holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Alfablot')
        ].start_date),
        None,
        "Remembering the fallen female ancestors and offerings to honor the family protective spirits",
        "The new moon after the Alfablot."
    ))

    holidays.append(Holiday(
        "Winters Nights Holy Tide",
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Alfablot')
        ].start_date,
        holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Disablot')
        ].start_date,
        "Starts a series of sacrifices celebrating love for friends and family and those who have fallen",
        "Start: Alfablot, End: Disablot"
    ))

    holidays.append(Holiday(
        "Welcome Goi and Freya",
        #feb 1st
        datetime.datetime(year, 2, 1),
        None,
        "Welcoming Goi and Freya into the home to warm up and thanking them for the spring time to come",
        "February 1st"
    ))

    holidays.append(Holiday(
        "Loki Day",
        #April 1st
        datetime.datetime(year, 4, 1),
        None,
        "A day for pranks and tricks, made in honor of the trickster god",
        "April 1st"
    ))

    holidays.append(Holiday(
        "Lokabrenna",
        #July 13th
        datetime.datetime(year, 7, 13),
        None,
        "Honoring Loki’s transformative fire, often involving rituals to 'burn away' stagnant energy or personal obstacles",
        "July 13th"
    ))

    holidays.append(Holiday(
        "Walpurgisnacht",
        #April 30th
        datetime.datetime(year, 4, 30),
        None,
        "Marks the official end of winter and the beginning of spring",
        "April 30th"
    ))

    holidays.append(Holiday(
        "Mayday",
        #May 1st
        datetime.datetime(year, 5, 1),
        None,
        "Celebrating the hope for triumph of our values: courageousness, solidarity, and generosity over selfishness and greed",
        "May 1st"
    ))

    previous_winter_solstice = datetime.datetime(phenoms_prev_json['data'][5]['year'],
                          phenoms_prev_json['data'][5]['month'],
                          phenoms_prev_json['data'][5]['day'])

    holidays.append(Holiday(
        "Charming of the Plough",
        #Halfway between Winter Solstice and Spring Equinox
        (previous_winter_solstice + (((holidays[
            next(i for i, x in enumerate(holidays) if x.name == 'Spring Equinox')
        ].start_date) - previous_winter_solstice) / 2)),
        None,
        "The preparation for the start of the planting season",
        "Halfway between previous Winter Solstice and Spring Equinox"
    ))

    # Add Sunwait holidays
    for each in range(6):
        sunwait = Holiday(
            "Sunwait",
            previous_thursday(holidays[
                next(i for i, x in enumerate(holidays) if x.name == 'Winter Solstice')
            ].start_date) - datetime.timedelta(days=each*7),
            None,
            "Each night celebrates the first 6 runes of Freya's Aett",
            "Start: 6th Thursday before Winter Solstice, End: Thursday before Winter Solstice"
        )
        holidays.append(sunwait)

    # Sort holidays by start date
    holidays = sorted(holidays, key=lambda holiday: holiday.start_date)
    return holidays

def get_holidays(year: int) -> List[Holiday]:
    """ Read holidays from DB for a given year. """
    conn = sqlite3.connect('norse_calendar.db')
    cursor = conn.cursor()
    if year not in [row[0] for row in cursor.execute('SELECT year FROM years').fetchall()]:
        logging.info("Holidays for year %d not found in DB. Generating...", year)
        write_holidays(year)
    logging.info("Retrieving holidays for year %d from DB.", year)
    cursor.execute('SELECT * FROM holidays WHERE start_date LIKE ?', (f'{year}%',))
    rows = cursor.fetchall()
    conn.close()
    return [Holiday(*row[1:]) for row in rows]

def write_holidays(year: int) -> None:
    """ Generate holidays for a given year and write to DB. """
    holidays = calculate_dates(year)
    # Write holidays to database
    conn = sqlite3.connect('norse_calendar.db')
    cursor = conn.cursor()
    if holidays is not None:
        for holiday in holidays:
            cursor.execute('''
                INSERT INTO holidays (name, start_date, end_date, description, schedule)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                holiday.name,
                holiday.start_date.strftime('%Y-%m-%d'),
                holiday.end_date.strftime('%Y-%m-%d') if holiday.end_date else None,
                holiday.description,
                holiday.schedule
            ))
        cursor.execute('''
                INSERT INTO years (year) VALUES (?)
        ''', (year,))
        conn.commit()
        conn.close()
        logging.info("Holidays for year %d written to DB.", year)
