""" Developer Menu for Testing Purposes. """
import logging
import tkinter as tk

def dev_menu():
    """ Developer Menu for Testing Purposes. """
    logging.info("Developer Menu Accessed")
    dev_dialog = tk.Tk()
    dev_dialog.title("Developer Menu")

    header = tk.Label(dev_dialog, text="Developer Menu", font=("Arial", 25))
    header.pack()


    dev_dialog.mainloop()
    logging.info("Developer Menu Closed")
