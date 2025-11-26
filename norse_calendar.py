""" Import Modules """
import datetime
import logging
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from typing import List
import tkcalendar
import urllib3
import certifi
from ics import Calendar, Event
from calculate_dates import calculate_dates, Holiday, check_api_connection

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

def download_latest_release():
    """ Open web browser to download latest release. """
    logging.info("Opening web browser to download latest release...")
    url = (
        "https://api.github.com/repos/"
        "michelfrancisbustillos/norsecalendar/releases/latest"
    )
    response = http.request("GET", url)
    latest_version = response.json()["name"]
    base = "https://github.com/michelfrancisbustillos/norsecalendar/releases/download/"
    exe = "/norse_calendar.exe"
    download_url = f"{base}{latest_version}{exe}"
    webbrowser.open(download_url)
    change_log_url = f"https://github.com/michelfrancisbustillos/norsecalendar/releases/tag/{latest_version}"
    webbrowser.open(change_log_url)

def update_check():
    """ Check for updates to the application. """
    logging.info("Checking for updates...")
    try:
        url = (
            "https://api.github.com/repos/"
            "michelfrancisbustillos/norsecalendar/releases/latest"
        )
        response = http.request("GET", url)
        latest_version = response.json()["name"]
        current_version = "v1.7.1"  # Current version of the application
        if latest_version != current_version:
            update_dialog = tk.Tk()
            update_dialog.title("Norse Calendar Calculator")

            header = tk.Label(update_dialog, text="Norse Calendar Calculator",
                              font=("Arial", 25))
            header.pack()

            link_text = "A new version is available. Click here to download."
            link = tk.Label(update_dialog, text=link_text,
                            fg="blue", cursor="hand2")
            link.pack()
            link.bind("<Button-1>", lambda e: download_latest_release())

            info_text = (f"Current version: {current_version}\n"
                         f"Latest version: {latest_version}")
            info = tk.Label(update_dialog, text=info_text)
            info.pack()

            ok_button = tk.Button(update_dialog, text="OK", command=update_dialog.destroy)
            ok_button.pack()

            update_dialog.mainloop()
            logging.info("Update available: %s", latest_version)
        else:
            logging.info("No updates available.")
    except urllib3.exceptions.MaxRetryError as update_error:
        logging.exception("Error checking for updates: %s", update_error)

class ToolTip:
    """ Tooltip class for Tkinter widgets. """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """ Display the tooltip. """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20  # Offset to position the tooltip
        y += self.widget.winfo_rooty() + 20

        # Create a Toplevel window for the tooltip
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """ Hide the tooltip. """
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

def generate_holidays(holidays: List[Holiday]) -> str:
    """ Generate Holiday summary string. """
    logging.info("Generating Holiday Summary")
    value = ""
    for holiday in holidays:
        value += str(holiday)
    return value

def generate_printable_summary(year_combobox: tk.Entry):
    """ Generate Printable Summary File """
    logging.info("Generating Printable Summary File")
    filename = filedialog.asksaveasfilename(
        title='Save as...',
        filetypes=[('Text files', '*.txt')],
        defaultextension='.txt'
    )
    year = int(year_combobox.get())
    holidays = calculate_dates(year)
    with open(filename, 'w', encoding="utf-8") as norse_calendar:
        norse_calendar.write(generate_holidays(holidays))
        logging.info("Printable Summary File Created")
    messagebox.showinfo("Summary Created", "Printable Summary File Created")

def generate_ics(year_combobox: tk.Entry):
    """ Generate ICS file for Calendar Import """
    logging.info("Generating ICS File")
    filename = filedialog.asksaveasfilename(
        title='Save as...',
        filetypes=[('Calendar files', '*.ics')],
        defaultextension='.ics'
    )
    year = int(year_combobox.get())
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

def submit(year_combobox: tk.Entry,
           summary: tk.Text,
           table: ttk.Treeview,
           generate_ics_button: tk.Button,
           generate_printable_button: tk.Button,
           calendar_widget: tkcalendar.Calendar,
           _event=None):
    """ Handle GUI Click Event. """
    try:
        year = int(year_combobox.get())
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
                event_details = (
                    f"{holiday.name}\n"
                    f"Description: {holiday.description}\n"
                    f"Schedule: {holiday.schedule}"
                )
                calendar_widget.calevent_create(holiday.start_date, event_details, 'holiday')
            calendar_widget.tag_config('holiday', background='lightblue', foreground='black')
            calendar_widget.config(state='normal',
                                   mindate=datetime.date((year-1), 12, 31),
                                   maxdate=datetime.date((year+1), 1, 1))
            calendar_widget.selection_set(datetime.date(year,
                                                        datetime.date.today().month,
                                                        datetime.date.today().day))
            generate_ics_button.config(state='normal')
            generate_printable_button.config(state='normal')
    except ValueError:
        messagebox.showerror("Invalid Input", "Year must be between 1700 and 2100.")
        year_combobox.delete(0, tk.END)
    return "break"

def clear(summary: tk.Text,
          table: ttk.Treeview,
          year_combobox: tk.Entry,
          generate_ics_button: tk.Button,
          generate_printable_button: tk.Button,
          calendar_widget: tkcalendar.Calendar):
    """ Clear summary and table views. """
    logging.info("Clearing GUI")
    summary.config(state='normal')
    summary.delete(1.0, tk.END)
    summary.config(state='disabled')
    table.delete(*table.get_children())
    year_combobox.delete(0, tk.END)
    generate_ics_button.config(state='disabled')
    generate_printable_button.config(state='disabled')
    calendar_widget.calevent_remove('all')
    calendar_widget.selection_set(datetime.date.today())
    calendar_widget.config(state='disabled')

def treeview_sort_column(tv, col, reverse):
    """ Sort Treeview Column. """
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    if col in ["Start", "End"]:
        l.sort(key=lambda t:
            datetime.datetime.strptime(t[0],
                                        '%m-%d-%Y') if t[0] else datetime.datetime.max,
               reverse=reverse)
    else:
        l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, text=col, command=lambda _col=col: \
                 treeview_sort_column(tv, _col, not reverse))

def show_calendar_event_details(calendar_widget: tkcalendar.Calendar):
    """ Show details of selected calendar event. """
    selected_date = calendar_widget.selection_get()
    logging.info("Selected Date: %s", selected_date.strftime('%m-%d-%Y'))
    event_ids = calendar_widget.get_calevents(selected_date)
    for event_id in event_ids:
        logging.info("Event ID: %s", event_id)
        event_text = calendar_widget.calevent_cget(event_id, option="text")
        messagebox.showinfo("Event Details",
                            f"Event: {event_text}\nDate: {selected_date.strftime('%m-%d-%Y')}")

def setup_gui():
    """ Setup the GUI components. """
    window = tk.Tk()
    window.title("Norse Calendar Calculator")

    header = tk.Label(text="Norse Calendar Calculator", font=("Arial", 25))
    header.pack()

    instructions = tk.Label(text="Select a year between 1700 and 2100:")
    instructions.pack()

    current_year = datetime.datetime.now().year
    years = [str(year) for year in range(1700, 2101)]
    year_combobox = ttk.Combobox(window, values=years)
    year_combobox.set(str(current_year))
    year_combobox.pack(pady=10)

    top_buttons = ttk.Frame(window)

    # helper functions to keep lambda lines short
    def do_submit(event=None):
        return submit(year_combobox, summary, table,
                      generate_ics_button, generate_printable_button,
                      calendar_widget, event)

    def do_clear():
        return clear(summary, table, year_combobox,
                     generate_ics_button, generate_printable_button,
                     calendar_widget)

    submit_button = tk.Button(top_buttons, text="Submit", command=do_submit)
    ToolTip(submit_button, "Submit the selected year.")
    submit_button.bind("<Button-1>", do_submit)

    clear_button = tk.Button(top_buttons, text="Clear", command=do_clear)
    ToolTip(clear_button, "Clear all fields.")

    window.bind('<Return>', do_submit)

    top_buttons.pack()
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
    table = ttk.Treeview(tab2, columns=columns, show='headings')

    # helper to produce short commands for sorting
    def make_sort_command(col_name):
        return lambda: treeview_sort_column(table, col_name, False)

    for col in columns:
        table.heading(col, text=col, command=make_sort_command(col))

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

    tab3 = ttk.Frame(tab_control)
    tab_control.add(tab3, text="Calendar")
    calendar_widget = tkcalendar.Calendar(tab3, selectmode='day', state='disabled')
    calendar_widget.bind("<<CalendarSelected>>",
                         lambda event: show_calendar_event_details(calendar_widget))
    calendar_widget.pack(fill="both", expand=True)
    tab_control.pack(expand=1, fill="both")

    bottom_buttons = ttk.Frame(window)
    generate_ics_button = tk.Button(bottom_buttons, text="Generate ICS",
                                command=lambda: generate_ics(year_combobox))
    ToolTip(generate_ics_button, "Generate an ICS file for calendar import.")
    generate_ics_button.config(state='disabled')
    generate_printable_button = tk.Button(bottom_buttons, text="Generate Printable Summary",
                                command=lambda: generate_printable_summary(year_combobox))
    ToolTip(generate_printable_button, "Generate a printable summary of the holidays.")
    generate_printable_button.config(state='disabled')
    bottom_buttons.pack()
    generate_ics_button.pack(side=tk.LEFT)
    generate_printable_button.pack()

    window.mainloop()

if __name__ == '__main__':
    update_check()
    check_api_connection()
    setup_gui()
    logging.info("Exiting Norse Calendar Calculator")
