"""
NorseCalendar UI
"""
import datetime
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import tkcalendar
from dev_menu import dev_menu
from generators import generate_summary, export_summary, generate_ics
from calculate_dates import get_holidays

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
                         background="#ffffe0", relief='solid', borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """ Hide the tooltip. """
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

class UI():
    """
    Generate UI and Handle Interaction
    """
    def __init__(self,window: tk.Tk):
        """
        Initialize UI
        
        :param self: Description
        :param window: Description
        :type window: tk.Tk
        """
        # Create GUI Elements
        self.window = window
        header = tk.Label(text="Norse Calendar Calculator", font=("Arial", 25))
        header.pack()
        year_frame1 = ttk.Frame(self.window)
        self.current_year = datetime.datetime.now().year
        start_label = tk.Label(year_frame1, text="Start Year:")
        start_label.pack(side=tk.LEFT)
        self.max_years = [str(self.year) for self.year in range(1701, 2101)]
        self.start_year_selector = ttk.Combobox(year_frame1, values=self.max_years)
        ToolTip(self.start_year_selector, "Select the start year (1701-2100)")
        self.start_year_selector.set(str(self.current_year))
        self.start_year_selector.pack(pady=10, side=tk.RIGHT)
        year_frame1.pack()
        year_frame2 = ttk.Frame(self.window)
        end_label = tk.Label(year_frame2, text="End Year:")
        end_label.pack(side=tk.LEFT)
        self.end_year_selector = ttk.Combobox(year_frame2, values=self.max_years)
        ToolTip(self.end_year_selector, "Select the end year (1701-2100)")
        self.end_year_selector.set(str(self.current_year))
        self.end_year_selector.pack(pady=10, side=tk.RIGHT)
        year_frame2.pack()
        top_buttons = ttk.Frame(self.window)
        submit_button = tk.Button(top_buttons, text="Submit", command=self.submit())
        ToolTip(submit_button, "Submit the selected year range.")
        clear_button = tk.Button(top_buttons, text="Clear", command=self.clear())
        ToolTip(clear_button, "Clear all fields.")
        top_buttons.pack()
        submit_button.pack(side=tk.LEFT)
        clear_button.pack()
        tab_control = ttk.Notebook(self.window)
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Summary')
        self.summary = tk.Text(tab1, state='disabled')
        yscrollbar = ttk.Scrollbar(tab1, orient="vertical", command=self.summary.yview)
        yscrollbar.pack(side="right", fill="y")
        self.summary.configure(yscrollcommand=yscrollbar.set)
        self.summary.pack(fill="both", expand=True)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab2, text="Table View")
        self.columns = ("Name", "Start", "End", "Description", "Schedule")
        self.table = ttk.Treeview(tab2, columns=self.columns, show='headings')
        self.reverse = False
        for self.col in self.columns:
            self.table.heading(self.col, text=self.col, command=self.treeview_sort_columns())

        self.table.heading("Name", text="Name")
        self.table.column("Name", minwidth=150, width=150, stretch=False)
        self.table.heading("Start", text="Start Date")
        self.table.column("Start", minwidth=100, width=100, stretch=False)
        self.table.heading("End", text="End Date")
        self.table.column("End", minwidth=100, width=100, stretch=False)
        self.table.heading("Description", text="Description")
        self.table.column("Description", minwidth=500, width=500, stretch=True)
        self.table.heading("Schedule", text="Schedule")
        self.table.column("Schedule", minwidth=500, width=500, stretch=True)

        yscrollbar = ttk.Scrollbar(tab2, orient="vertical", command=self.table.yview)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar = ttk.Scrollbar(tab2, orient="horizontal", command=self.table.xview)
        xscrollbar.pack(side="bottom", fill="x")

        self.table.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        self.table.pack(fill="both", expand=True)

        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab3, text="Calendar")
        self.calendar_widget = tkcalendar.Calendar(tab3, selectmode='day', state='disabled')
        self.calendar_widget.pack(fill="both", expand=True)
        tab_control.pack(expand=1, fill="both")

        bottom_buttons = ttk.Frame(self.window)
        self.generate_ics_button = tk.Button(bottom_buttons, text="Generate ICS",
                                    command=lambda: generate_ics(self.start_year_selector,
                                                                self.end_year_selector))
        ToolTip(self.generate_ics_button, "Generate an ICS file for calendar import.")
        self.generate_ics_button.config(state='disabled')
        self.generate_printable_button = tk.Button(bottom_buttons, text="Export Summary",
                                    command=lambda: export_summary(self.summary))
        ToolTip(self.generate_printable_button, "Export a printable summary file.")
        self.generate_printable_button.config(state='disabled')
        bottom_buttons.pack()
        self.generate_ics_button.pack(side=tk.LEFT)
        self.generate_printable_button.pack()
        dev_button = tk.Button(self.window, text="π", command=dev_menu)
        dev_button.pack(side=tk.RIGHT)

        #Bind UI Elements
        submit_button.bind("<Button-1>", self.submit())
        self.start_year_selector.bind("<<ComboboxSelected>>", self.combo_box_selected())
        self.end_year_selector.bind("<<ComboboxSelected>>", self.combo_box_selected())
        self.calendar_widget.bind("<<CalendarSelected>>",
                        lambda event: self.show_calendar_event_details())

    def submit(self):
        """
        Handle Submit Button Press or 'Enter'
        
        :param self: Description
        """
        try:
            if not 1700 < int(self.start_year_selector.get()) < 2100:
                logging.error("%s is not a valid start year.", int(self.start_year_selector.get()))
                raise ValueError("Start year must be a number between 1701 and 2100")
            if not 1700 < int(self.end_year_selector.get()) < 2100:
                logging.error("%s is not a valid end year.", int(self.end_year_selector.get()))
                raise ValueError("End year must be a number between 1701 and 2100")

            logging.info("Calculating holidays...")
            logging.info("Start Year: %d, End Year: %d",
                            int(self.start_year_selector.get()),
                            int(self.end_year_selector.get()))
            years = [int(self.start_year_selector.get())] if int(self.end_year_selector.get()) == int(self.start_year_selector.get()) else list(range(int(self.start_year_selector.get()), int(self.end_year_selector.get())+1))
            for year in years:
                logging.info("Requesting Year: %s", year)
                self.summary.config(state='normal')
                holidays = get_holidays(year)
                if holidays is None:
                    logging.error("No holidays calculated for year %d.", year)
                    self.summary.insert(1.0,
                                    f"No holidays calculated for {year}. See log for details.\n")
                else:
                    self.summary.insert(1.0, generate_summary(holidays))
                    self.summary.config(state='disabled')
                    for holiday in holidays:
                        clean_end_date = holiday.end_date if holiday.end_date else ""
                        clean_description = holiday.description if holiday.description else ""
                        clean_schedule = holiday.schedule if holiday.schedule else ""

                        self.table.insert("",
                                    tk.END,
                                    text=holiday.name,
                                    values=(holiday.name,
                                            holiday.start_date,
                                            clean_end_date,
                                            clean_description,
                                            clean_schedule))
                        event_details = (
                            f"{holiday.name}\n"
                            f"Description: {holiday.description}\n"
                            f"Schedule: {holiday.schedule}"
                        )

                        self.calendar_widget.calevent_create(datetime.datetime.strptime(str(holiday.start_date), '%Y-%m-%d'), event_details, 'holiday')
            self.calendar_widget.tag_config('holiday', background='lightblue', foreground='black')
            self.calendar_widget.config(state='normal',
                                    mindate=datetime.date((int(self.start_year_selector.get())-1),
                                                            12,
                                                            31),
                                    maxdate=datetime.date((int(self.end_year_selector.get())+1),
                                                          1,
                                                          1))
            self.calendar_widget.selection_set(datetime.date(self.current_year,
                                                        datetime.date.today().month,
                                                        datetime.date.today().day))
            self.generate_ics_button.config(state='normal')
            self.generate_printable_button.config(state='normal')
        except ValueError:
            messagebox.showerror("Invalid Input", "Year must be between 1700 and 2100.")
            self.start_year_selector.delete(0, tk.END)
            self.end_year_selector.delete(0, tk.END)
        return "break"


    def clear(self):
        """
        Handle Clear Button Press
        
        :param self: Description
        """
        logging.info("Clearing GUI")
        self.summary.config(state='normal')
        self.summary.delete(1.0, tk.END)
        self.summary.config(state='disabled')
        self.table.delete(*self.table.get_children())
        self.start_year_selector.set(str(datetime.datetime.now().year))
        self.end_year_selector.set(str(datetime.datetime.now().year))
        self.generate_ics_button.config(state='disabled')
        self.generate_printable_button.config(state='disabled')
        self.calendar_widget.calevent_remove('all')
        self.calendar_widget.selection_set(datetime.date.today())
        self.calendar_widget.config(state='disabled')
        return "break"

    def combo_box_selected(self):
        """
        Handle Combobox Imput Checking
        
        :param self: Description
        """
        start_year = self.start_year_selector.get()
        end_year = self.end_year_selector.get()
        if start_year > end_year:
            self.end_year_selector.set(start_year)
        if end_year < start_year:
            self.end_year_selector.set(start_year)

    def treeview_sort_columns(self):
        """
        Sort Treeview columns on click
        
        :param self: Description
        """
        l = [(self.table.set(k, self.col), k) for k in self.table.get_children('')]
        logging.info("Sorting column: %s, Reverse: %s", self.col, self.reverse)
        if self.col in ["Start", "End"]:
            l.sort(key=lambda t:
                datetime.datetime.strptime(t[0],
                                            '%m-%d-%Y') if t[0] else datetime.datetime.max,
                reverse=self.reverse)
        else:
            l.sort(reverse=self.reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.table.move(k, '', index)

        # reverse sort next time
        self.table.heading(self.col, text=self.col, command=lambda _col=self.col: \
                    self.treeview_sort_columns())
        return "break"

    def show_calendar_event_details(self):
        """
        Handle event details display on date click
        
        :param self: Description
        """
        selected_date = self.calendar_widget.selection_get()
        if selected_date is not None:
            logging.info("Displaying details for date: %s", selected_date.strftime('%m-%d-%Y'))
            event_ids = self.calendar_widget.get_calevents(selected_date)
            for event_id in event_ids:
                event_text = self.calendar_widget.calevent_cget(event_id, option="text")
                messagebox.showinfo("Event Details",
                                    f"Event: {event_text}\nDate: {selected_date.strftime('%m-%d-%Y')}")
        else:
            logging.info("No date selected, but function called")
