""" Import Modules """
import datetime
from dataclasses import dataclass
import logging
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from typing import List, Optional
import certifi
import urllib3
from ics import Calendar, Event

# Initialize HTTP Pool Manager
http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

# Configure logging
logging.basicConfig(filename="debug.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logging.info("Starting Norse Calendar Calculator")

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

def check_api_connection() -> bool:
    """ Check API Connection. """
    try:
        http.request("GET", "https://aa.usno.navy.mil/api/")
        logging.info("API Connection Successful")
        return True
    except urllib3.exceptions.MaxRetryError:
        messagebox.showerror("API Connection Error",
                             "Could not connect to the API. Please check your internet connection.")
        logging.error("API Connection Error")
        sys.exit(1)

def calculate_dates(year: int) -> List[Holiday]:
    """ Calculate Holiday dates and return array of class Holiday. """
    holidays = [None] * 26  # Preallocate list for 26 holidays

    # Get Core Dates
    phenom_api = f"https://aa.usno.navy.mil/api/seasons?year={year}&tz=-6&dst=true"
    phenoms = http.request("GET", phenom_api)
    phenoms_json = phenoms.json()

    phenom_api_prev = f"https://aa.usno.navy.mil/api/seasons?year={year-1}&tz=-6&dst=true"
    phenoms_prev = http.request("GET", phenom_api_prev)
    phenoms_prev_json = phenoms_prev.json()

    # Create Holiday objects for equinoxes and solstices
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

    start_day = datetime.date(year, 1, 1)
    logging.info("Start Day: %s", start_day.strftime('%m-%d-%Y'))
    moon_api = f"https://aa.usno.navy.mil/api/moon/phases/date?date={start_day}&nump=99"
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

def generate_holidays(holidays: List[Holiday]) -> str:
    """ Generate Holiday summary string. """
    value = ""
    for holiday in holidays:
        value += str(holiday)
    return value

def generate_ics(year_entry: tk.Entry):
    """ Generate ICS file for Calendar Import """
    logging.info("Generating ICS File")
    filename = filedialog.asksaveasfilename(
        title='Save as...',
        filetypes=[('Calendar files', '*.ics')],
        defaultextension='.ics'
    )
    year = int(year_entry.get())
    holidays = calculate_dates(year)
    calendar = Calendar()
    for holiday in holidays:
        event = Event()
        event.name = holiday.name
        event.begin = holiday.start_date
        event.description = f"Description: {holiday.description}\nSchedule: {holiday.schedule}"
        if holiday.end_date is not None:
            event.end = holiday.end_date
        event.make_all_day()
        calendar.events.add(event)
    with open(filename, 'w', encoding="utf-8") as norse_calendar:
        norse_calendar.writelines(calendar.serialize_iter())
        logging.info("ICS File Created")
    messagebox.showinfo("ICS Created", "ICS File Created")

def submit(year_entry: tk.Entry,
           summary: tk.Text,
           table: ttk.Treeview,
           generate_button: tk.Button,
           _event=None):
    """ Handle GUI Click Event. """
    try:
        year = int(year_entry.get())
        if year < 1700 or year > 2100:
            logging.error("%s is not a valid year.", year)
            raise ValueError("Year must be a number between 1700 and 2100")
        else:
            logging.info("Year: %s", year)
            summary.config(state='normal')
            holidays = calculate_dates(year)
            summary.insert(1.0, generate_holidays(holidays))
            summary.config(state='disabled')
            for holiday in holidays:
                clean_end_date = holiday.end_date.strftime('%m-%d-%Y') if holiday.end_date else ""
                clean_description = holiday.description if holiday.description else ""
                clean_schedule = holiday.schedule if holiday.schedule else ""

                table.insert("",
                             tk.END,
                             text=holiday.name,
                             values=(holiday.name,
                                     holiday.start_date.strftime('%m-%d-%Y'),
                                     clean_end_date,
                                     clean_description,
                                     clean_schedule))

            generate_button.config(state='normal')
    except ValueError:
        messagebox.showerror("Invalid Input", "Year must be between 1700 and 2100.")
        year_entry.delete(0, tk.END)
    return "break"

def clear(summary: tk.Text, table: ttk.Treeview, year_entry: tk.Entry, generate_button: tk.Button):
    """ Clear summary and table views. """
    logging.info("Clearing GUI")
    summary.config(state='normal')
    summary.delete(1.0, tk.END)
    summary.config(state='disabled')
    table.delete(*table.get_children())
    year_entry.delete(0, tk.END)
    generate_button.config(state='disabled')
    
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, text=col, command=lambda _col=col: \
                 treeview_sort_column(tv, _col, not reverse))

def setup_gui():
    """ Setup the GUI components. """
    window = tk.Tk()
    window.title("Norse Calendar Calculator")

    header = tk.Label(text="Norse Calendar Calculator", font=("Arial", 25))
    header.pack()

    instructions = tk.Label(text="Enter a year between 1700 and 2100:")
    instructions.pack()

    year_entry = tk.Entry(width=50)
    year_entry.pack()

    buttons = ttk.Frame(window)
    submit_button = tk.Button(buttons,
                              text="Submit",
                              command=lambda: submit(year_entry, summary, table, generate_button))
    submit_button.bind("<Button-1>",
                       lambda event: submit(year_entry, summary, table, generate_button, event))
    clear_button = tk.Button(buttons, text="Clear",
                             command=lambda: clear(summary, table, year_entry, generate_button))
    window.bind('<Return>',
                lambda event: submit(year_entry, summary, table, generate_button, event))
    buttons.pack()
    submit_button.pack(side=tk.LEFT)
    clear_button.pack()

    tab_control = ttk.Notebook(window)
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Summary')
    summary = tk.Text(tab1, state='disabled')
    yscrollbar = ttk.Scrollbar(tab1, orient="vertical", command=summary.yview)
    yscrollbar.pack(side="right", fill="y")
    summary.configure(yscrollcommand=yscrollbar.set)
    summary.pack(fill="both", expand=True)

    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text="Table View")
    columns = ("Name", "Start", "End", "Description", "Schedule")
    table = ttk.Treeview(tab2,
                         columns=columns,
                         show='headings')

    for col in columns:
        table.heading(col, text=col, command=lambda _col=col: \
                        treeview_sort_column(table, _col, False))

    table.heading("Name", text="Name")
    table.column("Name", minwidth=150, width=150, stretch=False)
    table.heading("Start", text="Start Date")
    table.column("Start", minwidth=100, width=100, stretch=False)
    table.heading("End", text="End Date")
    table.column("End", minwidth=100, width=100, stretch=False)
    table.heading("Description", text="Description")
    table.column("Description", minwidth=500, width=500, stretch=True)
    table.heading("Schedule", text="Schedule")
    table.column("Schedule", minwidth=500, width=500, stretch=True)

    yscrollbar = ttk.Scrollbar(tab2, orient="vertical", command=table.yview)
    yscrollbar.pack(side="right", fill="y")
    xscrollbar = ttk.Scrollbar(tab2, orient="horizontal", command=table.xview)
    xscrollbar.pack(side="bottom", fill="x")

    table.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    table.pack(fill="both", expand=True)
    tab_control.pack(expand=1, fill="both")
    generate_button = tk.Button(text="Generate ICS",
                                command=lambda: generate_ics(year_entry))
    generate_button.config(state='disabled')
    generate_button.pack(side=tk.BOTTOM)

    window.mainloop()

if __name__ == '__main__':
    check_api_connection()
    setup_gui()
    logging.info("Exiting Norse Calendar Calculator")
