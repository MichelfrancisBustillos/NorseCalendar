""" Import Modules"""
import datetime
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import certifi
import urllib3

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

class Holiday():
    """ Class containing definition of 'Holiday' object."""
    def __init__(self, name, start_date, end_date=None, desc=None, schedule=None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.description = desc
        self.schedule = schedule

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
        if self.schedule is not None:
            print("Schedule: ", self.schedule)
            value = value + "Schedule: " + self.schedule + "\n"
        return value

@dataclass
class MoonPhase():
    """ Class defining moonphase."""
    phase: str
    date: datetime

def calculate_dates(year):
    """ Calculate Holiday dates and return array of class Holiday."""
    holidays = [None] * 20
    #Get Core Dates
    phenom_api = "https://aa.usno.navy.mil/api/seasons?year=" + str(year) + "&tz=-6&dst=true"
    phenoms = http.request("GET", phenom_api)
    phenoms_json = phenoms.json()

    holidays[0] = Holiday(
        "Spring Equinox",
        datetime.datetime(phenoms_json['data'][1]['year'],
                        phenoms_json['data'][1]['month'],
                        phenoms_json['data'][1]['day']))
    holidays[1] = Holiday(
        "Summar Solstice",
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
    holidays[4] = Holiday(
        "Yule",
        holidays[3].start_date,
        holidays[3].start_date + datetime.timedelta(days=12),
        None,
        "Start: Winter Solstice, End: 12 days after the Winter Solstice.")
    holidays[5] = Holiday(
        "Thorrablot",
        next_full_moon(next_new_moon(holidays[3].start_date)),
        None,
        None,
        "The full moon after the new moon following the Winter Solstice.")
    holidays[6] = Holiday(
        "Disting",
        next_full_moon(holidays[5].start_date),
        None,
        None,
        "The full moon after the Thorrablot.")
    holidays[7] = Holiday(
        "Mid-Winter",
        holidays[5].start_date,
        next_new_moon(holidays[5].start_date),
        None,
        "Start: Thorrablot, End: Next New Moon")
    holidays[8] = Holiday(
        "Lenzen",
        previous_full_moon(holidays[0].start_date),
        next_full_moon(holidays[0].start_date),
        None,
        "Start: Full moon before the Spring Equinox, End: Full moon after the Spring Equinox")
    holidays[9] = Holiday(
        "Offering to Freya",
        holidays[0].start_date,
        None,
        None,
        "The Spring Equinox")
    holidays[10] = Holiday(
        "Ostara",
        next_full_moon(holidays[0].start_date),
        None,
        None,
        "The full moon after the Spring Equinox.")
    holidays[11] = Holiday(
        "Sigrblot",
        next_new_moon(holidays[10].start_date),
        None,
        None,
        "The new moon after Ostara.")
    holidays[12] = Holiday(
        "Summer Nights Holy Tide",
        holidays[10].start_date,
        holidays[11].start_date,
        None,
        "Start: Ostara, End: Sigrblot")
    holidays[13] = Holiday(
        "Mid-Summer",
        holidays[1].start_date,
        None,
        None,
        "The Summer Solstice")
    holidays[14] = Holiday(
        "Lammas",
        closest_full_moon(holidays[2].start_date),
        None,
        None,
        "The full moon closest to the Fall Equinox.")
    holidays[15] = Holiday(
        "Hausblot",
        next_new_moon(holidays[14].start_date),
        None,
        None,
        "The new moon after Lammas.")
    holidays[16] = Holiday(
        "Harvest Home Holy Tide",
        holidays[14].start_date,
        holidays[15].start_date,
        None,
        "Start: Lammas, End: Hausblot")
    holidays[17] = Holiday(
        "Alfablot",
        next_full_moon(next_full_moon(holidays[2].start_date)),
        None,
        None,
        "The two full moons after the fall Equinox.")
    holidays[18] = Holiday(
        "Disablot",
        next_new_moon(holidays[17].start_date),
        None,
        None,
        "The new moon after the Alfablot.")
    holidays[19] = Holiday(
        "Winters Nights Holy Tide",
        holidays[17].start_date,
        holidays[18].start_date,
        None,
        "Start: Alfablot, End: Disblot")
    return holidays

def print_holidays(holidays):
    """ Generate Holiday summary string."""
    value = ""
    counter = 0
    for each in holidays:
        value = value + holidays[counter].print()
        counter = counter + 1
    return value
#GUI
def submit(_event):
    """ Handle GUI Click Event."""
    try:
        year = int(year_entry.get())
        if year < 1700 or year > 2100:
            raise ValueError("Year must be a number between 1700 and 2100")
        else:
            print(year)
            summary.config(state='normal')
            holidays = calculate_dates(year)
            summary.insert(1.0, print_holidays(holidays))
            summary.config(state='disabled')
    except ValueError:
        messagebox.showerror("Invalid Input", "Year must between 1700 and 2100.")
        year_entry.delete(0,tk.END)
    return "break"

window = tk.Tk()
window.state('zoomed')
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
tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text = 'Summary')
tab_control.pack(expand=1, fill="both")
summary = tk.Text(tab1, state='disabled')
summary.pack(fill="both",expand=True)
window.title("Norse Calendar Calculator")
window.mainloop()
