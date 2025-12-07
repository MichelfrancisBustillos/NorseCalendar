"""
Generate Outputs
"""
import logging
from typing import List
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from ics import Calendar, Event
from calculate_dates import Holiday, get_holidays

def generate_summary(holidays: List[Holiday]) -> str:
    """ Generate Holiday summary string. """
    logging.info("Generating Holiday Summary")
    summary = ""
    for holiday in holidays:
        value = f"Name: {holiday.name}\n"
        if holiday.start_date is None:
            logging.error("Date Missing!")
            value += "Date: Missing\n"
        elif holiday.end_date is None:
            value += f"Date: {holiday.start_date}\n"
        else:
            value += f"Start Date: {holiday.start_date}\n"
            value += f"End Date: {holiday.end_date}\n"
        if holiday.description is not None:
            value += f"Description: {holiday.description}\n"
        if holiday.schedule is not None:
            value += f"Schedule: {holiday.schedule}\n"
        summary += value
    return summary

def export_summary(summary: tk.Text,):
    """ Export Summary File """
    logging.info("Exporting Summary File")
    filename = filedialog.asksaveasfilename(
        title='Save as...',
        filetypes=[('Text files', '*.txt')],
        defaultextension='.txt'
    )
    with open(filename, 'w', encoding="utf-8") as norse_calendar:
        norse_calendar.write(summary.get(1.0, tk.END))
        logging.info("Summary File Created")
    messagebox.showinfo("Summary Created", "Summary Export Created")

def generate_ics(start_year_selector: ttk.Combobox, end_year_selector: ttk.Combobox):
    """ Generate ICS file for Calendar Import """
    logging.info("Generating ICS File")
    filename = filedialog.asksaveasfilename(
        title='Save as...',
        filetypes=[('Calendar files', '*.ics')],
        defaultextension='.ics'
    )
    holidays = []
    for year in range(int(start_year_selector.get()), int(end_year_selector.get()) + 1):
        holidays.extend(get_holidays(year))
    calendar = Calendar()
    for holiday in holidays:
        event = Event()
        event.name = holiday.name
        event.begin = datetime.datetime.strptime(holiday.start_date, '%Y-%m-%d')
        event.description = f"Description: {holiday.description}\nSchedule: {holiday.schedule}"
        if holiday.end_date is not None:
            event.end = datetime.datetime.strptime(holiday.end_date, '%Y-%m-%d')
        event.make_all_day()
        calendar.events.add(event)
        print("Added event to calendar:", holiday.name)
    with open(filename, 'w', encoding="utf-8") as norse_calendar:
        norse_calendar.writelines(calendar.serialize_iter())
        logging.info("ICS File Created")
    messagebox.showinfo("ICS Created", "ICS File Created")
