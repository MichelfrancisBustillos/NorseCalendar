""" Import Modules """
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
import logging
import webbrowser
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox
import urllib3
import certifi
from UI import UI

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
        latest_version = latest_version.replace("v", "")
        current_version = "2.0.0"  # Current version of the application
        if latest_version > current_version:
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
            logging.warning("Update available: %s", latest_version)
        elif latest_version < current_version:
            update_dialog = tk.Tk()
            update_dialog.title("Norse Calendar Calculator")

            header = tk.Label(update_dialog, text="Norse Calendar Calculator",
                              font=("Arial", 25))
            header.pack()
            warning_label = tk.Label(update_dialog,
                                     text="You are using a beta version!",
                                     fg="red")
            warning_label.pack()
            link_text = "Click here to download the latest stable version."
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
            logging.warning("Beta Version In Use! %s", current_version)
        else:
            logging.info("No updates available.")
    except urllib3.exceptions.MaxRetryError as update_error:
        logging.exception("Error checking for updates: %s", update_error)

def db_setup():
    """ Set up the SQLite database for storing holidays. """
    conn = sqlite3.connect('norse_calendar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holidays (
            id INTEGER PRIMARY KEY,
            name TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT,
            schedule TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS years (
            id INTEGER PRIMARY KEY,
            year INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moon_phases (
            id INTEGER PRIMARY KEY,
            phase TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database setup complete.")

def check_api_connection() -> bool:
    """ Check API Connection. """
    try:
        http.request("GET", "https://aa.usno.navy.mil/api/")
        logging.info("API Connection Successful")
        return True
    except urllib3.exceptions.MaxRetryError:
        err_msg = ("Could not connect to the API. "
                   "Please check your internet connection.")
        messagebox.showerror("API Connection Error", err_msg)
        logging.error("API Connection Error")
        sys.exit(1)

if __name__ == '__main__':
    update_check()
    check_api_connection()
    db_setup()
    #setup_gui()
    logging.info("Setting up GUI")
    window = tk.Tk()
    window.title("Norse Calendar Calculator")
    ui = UI(window)
    window.mainloop()
    logging.info("Exiting Norse Calendar Calculator")
