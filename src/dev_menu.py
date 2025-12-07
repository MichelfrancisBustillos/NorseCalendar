""" Developer Menu for Testing Purposes. """
import logging
import tkinter as tk

def dev_menu():
    """ Developer Menu for Testing Purposes. """
    logging.info("Developer Menu Accessed")
    dev_dialog = tk.Tk()
    dev_dialog.title("Lo There...")

    poem = """Lo, there do I see my father.
Lo, there do I see my mother, and my sisters, and my brothers.
Lo, there do I see the line of my people, back to the beginning.
Lo, they do call to me.
They bid me take my place among them,
In the halls of Valhalla, Where the brave may live forever
"""

    text = tk.Text(dev_dialog)
    text.insert("1.0", poem)
    text.config(state="disabled")
    text.pack()
    dev_dialog.mainloop()
    logging.info("Developer Menu Closed")
