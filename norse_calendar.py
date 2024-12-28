""" Import Modules"""
import datetime
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox
import certifi
import urllib3

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)


class Holiday():
    """ Class containing definition of 'Holiday' object."""
    def __init__(self, name, start_date, end_date=None, desc=None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = desc

    def print(self):
        """ Method to print holiday class contents."""
        value = "Name: " + self.name + "\n"
        print("Name:", self.name)
        if self.start_date is None:
            print("Date: Missing")
            value = value + "Date: Missing\n"
        elif self.end_date is None:
            print("Date:", self.start_date.strftime('%m-%d-%Y'))
            value = value + "Date: " + self.start_date.strftime('%m-%d-%Y') + "\n"
        else:
            print("Start Date:", self.start_date.strftime('%m-%d-%Y'))
            value = value + "Start Date: " + self.start_date.strftime('%m-%d-%Y') + "\n"
            print("End Date:", self.end_date.strftime('%m-%d-%Y'))
            value = value + "End Date: " + self.end_date.strftime('%m-%d-%Y') + "\n"
        if self.description is not None:
            print("Description:", self.description)
            value = value + "Description: " + self.description + "\n"
        return value

@dataclass
class MoonPhase():
    """ Class defining moonphase."""
    phase: str
    date: datetime

def main(year):
    """ Core Program Functions"""
    #Get Core Dates
    phenom_api = "https://aa.usno.navy.mil/api/seasons?year=" + str(year) + "&tz=-6&dst=true"
    phenoms = http.request("GET", phenom_api)
    phenoms_json = phenoms.json()

    spring_equinox = Holiday(
        "Spring Equinox",
        datetime.datetime(phenoms_json['data'][1]['year'],
                        phenoms_json['data'][1]['month'],
                        phenoms_json['data'][1]['day']))
    summer_solstice = Holiday(
        "Summar Solstice",
        datetime.datetime(phenoms_json['data'][2]['year'],
                        phenoms_json['data'][2]['month'],
                        phenoms_json['data'][2]['day']))
    fall_equinox = Holiday(
        "Fall Equinox",
        datetime.datetime(phenoms_json['data'][4]['year'],
                            phenoms_json['data'][4]['month'],
                            phenoms_json['data'][4]['day']))
    winter_solstice = Holiday(
        "Winter Solstice",
        datetime.datetime(phenoms_json['data'][5]['year'],
                        phenoms_json['data'][5]['month'],
                        phenoms_json['data'][5]['day']))

    start_day = datetime.date(int(year), 1, 1)
    print("Start Day:", start_day.strftime('%m-%d-%Y'))
    moon_api = "https://aa.usno.navy.mil/api/moon/phases/date?date=" + str(start_day) + "&nump=99"
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

    def next_new_moon(input_date):
        """ Get Next New Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "New Moon":
                return moon_counter.date

    def next_full_moon(input_date):
        """ Get Next Full Moon Date."""
        for moon_counter in all_moons:
            if moon_counter.date > input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date

    def previous_full_moon(input_date):
        """ Get Previous Full Moon Date."""
        for moon_counter in reversed(all_moons):
            if moon_counter.date < input_date and moon_counter.phase == "Full Moon":
                return moon_counter.date

    def closest_full_moon(input_date):
        """ Get Closest Full Moon Date."""
        days_before = input_date - previous_full_moon(input_date)
        days_after = next_full_moon(input_date) - input_date
        if days_before < days_after:
            return previous_full_moon(input_date)
        else:
            return next_full_moon(input_date)

    #Calculate Holidays
    yule = Holiday(
        "Yule",
        winter_solstice.start_date,
        winter_solstice.start_date + datetime.timedelta(days=12))
    thorrablot = Holiday(
        "Thorrablot",
        next_full_moon(next_new_moon(winter_solstice.start_date)))
    disting = Holiday(
        "Disting",
        next_full_moon(thorrablot.start_date))
    midwinter = Holiday(
        "Mid-Winter",
        thorrablot.start_date,
        next_new_moon(thorrablot.start_date))
    lenzen = Holiday(
        "Lenzen",
        previous_full_moon(spring_equinox.start_date),
        next_full_moon(spring_equinox.start_date))
    offering_to_freya = Holiday(
        "Offering to Freya",
        spring_equinox.start_date)
    ostara = Holiday(
        "Ostara",
        next_full_moon(spring_equinox.start_date))
    sigrblot = Holiday(
        "Sigrblot",
        next_new_moon(ostara.start_date))
    summer_tides = Holiday(
        "Summer Nights Holy Tide",
        ostara.start_date, sigrblot.start_date)
    midsummer = Holiday(
        "Mid-Summer",
        summer_solstice.start_date)
    lammas = Holiday(
        "Lammas",
        closest_full_moon(fall_equinox.start_date))
    hausblot = Holiday(
        "Hausblot",
        next_new_moon(lammas.start_date))
    harvest_tides = Holiday(
        "Harvest Home Holy Tide",
        lammas.start_date, hausblot.start_date)
    alfablot = Holiday(
        "Alfablot",
        next_full_moon(next_full_moon(fall_equinox.start_date)))
    disablot = Holiday(
        "Disablot",
        next_new_moon(alfablot.start_date))
    winters_tides = Holiday(
        "Winters Nights Holy Tide",
        alfablot.start_date,
        disablot.start_date)

    #Output Holidays
    date_list = (spring_equinox.print()+
                 summer_solstice.print()+
                 fall_equinox.print()+
                 winter_solstice.print()+
                 yule.print()+
                 thorrablot.print()+
                 disting.print()+
                 midwinter.print()+
                 lenzen.print()+
                 offering_to_freya.print()+
                 ostara.print()+
                 sigrblot.print()+
                 summer_tides.print()+
                 midsummer.print()+
                 lammas.print()+
                 hausblot.print()+
                 harvest_tides.print()+
                 alfablot.print()+
                 disablot.print()+
                 winters_tides.print())

    return date_list

#GUI
def submit(_event):
    """ Handle GUI Click Event."""
    try:
        year = int(year_entry.get())
        if year < 1700 or year > 2100:
            raise ValueError("Year must be a number between 1700 and 2100")
        else:
            print(year)
            content["text"] = main(year)
    except ValueError:
        messagebox.showerror("Invalid Input", "Year must between 1700 and 2100.")
        year_entry.delete(0,tk.END)
    return "break"

window = tk.Tk()
header = tk.Label(text="Norse Calendar Calculator",font=("Arial", 25))
header.pack()
instructions = tk.Label(text="Enter a year between 1700 and 2100:")
instructions.pack()
year_entry = tk.Entry(width=50)
year_entry.pack()
submit_button = tk.Button(text="Submit")
submit_button.bind("<Button-1>", submit)
window.bind('<Return>', submit)
submit_button.pack()
content = tk.Label()
content.pack()
window.title("Norse Calendar Calculator")
window.mainloop()
