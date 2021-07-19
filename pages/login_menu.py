import main
import tkinter as tk
from tkinter import messagebox
import hashlib
import sqlite3
from main import font_28, DARK_GREY, ACCENT_COLOUR, LIGHT_GREY, res_height, res_width, SMALL_FONT


class LoginMenu(tk.Frame):  # login menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=main.DARK_GREY)

    def load_page(self):
        # load the main menu with the entered user
        def load_main():
            username = usr.get()  # get the entered username
            password = hashlib.sha256(pwd.get().encode('utf-8')).hexdigest()  # hash the entered password
            conn = sqlite3.connect("data/logins.db")  # connect to the local database
            c = conn.cursor()
            c.execute('SELECT * FROM logins')
            data = c.fetchall()  # retrieve all possible logins
            conn.commit()
            conn.close()
            for row in data:  # loop through logins to compare the username and hash
                if row[1] == username and row[2] == password:
                    main.user_id = row[0]  # set the user ID
                    print("Login by: " + row[0])
                    MainMenu.load_page(main.app.frames[MainMenu])  # load the main menu
                    self.update_idletasks()  # make page transition less choppy
                    main.app.show_frame(MainMenu)
                    return True  # successful login
            messagebox.showerror(title="Invalid Login", message="The username or password you entered is incorrect.")
            return False  # unsuccessful login

        # login entries
        usr = tk.Entry(self, font=font_28, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        usr.place(relx=0.35, rely=0.32, width=0.3 * res_width, height=0.1 * res_height)

        pwd = tk.Entry(self, font=font_28, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        pwd.place(relx=0.35, rely=0.42, width=0.3 * res_width, height=0.1 * res_height)

        tk.Button(self, text="Login", font=font_28, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: load_main()).place(relx=0.45, rely=0.52)

        # new user
        tk.Button(self, text="Add User", font=SMALL_FONT, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: main.app.show_frame(NewUser)).place(relx=0.876, rely=0.925)
