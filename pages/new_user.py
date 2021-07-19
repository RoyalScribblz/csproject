import main
import tkinter as tk
from main import DARK_GREY, font_20, ACCENT_COLOUR, LIGHT_GREY
import uuid
import hashlib
import sqlite3
import json
from login_menu import LoginMenu


class NewUser(tk.Frame):  # user creation menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=DARK_GREY)

        # data entries
        tk.Label(self, text="New User", font=font_20, fg=ACCENT_COLOUR, bg=DARK_GREY) \
            .pack(pady=(main.rel_height(0.45), 0))

        usr = tk.Entry(self, font=font_20, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        usr.pack(pady=(main.rel_height(0.1), 0))

        pwd = tk.Entry(self, font=font_20, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        pwd.pack(pady=(2, 0))

        def create_user():
            passwd = hashlib.sha256(pwd.get().encode('utf-8')).hexdigest()  # hash the password entry
            conn = sqlite3.connect("logins.db")
            c = conn.cursor()
            new_uuid = str(uuid.uuid1())
            c.execute("INSERT INTO logins VALUES (?, ?, ?)", (new_uuid, usr.get(), passwd))  # write to the database
            c.execute('SELECT * FROM logins')
            conn.commit()
            conn.close()
            main.app.show_frame(LoginMenu)  # go back to the login menu

            with open("data/settings.json", "r") as settings_file:  # create a default settings profile for the new user
                settings = json.load(settings_file)  # get settings
                settings.append({"uuid": new_uuid, "favourites": ["BTC", "ETH", "XRP", "LTC", "LINK", "ADA"]})  # add
            with open("data/settings.json", "w") as settings_file:
                json.dump(settings, settings_file, indent=4)  # write new settings

        tk.Button(self, text="Create", font=font_20, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: create_user()).pack(pady=(main.rel_height(0.1), 0))