import main
from login_menu import LoginMenu
import tkinter as tk
from main import DARK_GREY, LARGE_FONT, ACCENT_COLOUR, SMALL_FONT, LIGHT_GREY


class Startup(tk.Frame):  # startup page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.configure(bg=DARK_GREY)  # background colour

        # set the resolution variables and load the login menu
        def load_main():
            main.res_width = self.winfo_width()
            main.res_height = self.winfo_height()

            main.font_28 = ("Consolas", round(main.res_height / 28))
            main.font_20 = ("Consolas", round(main.res_height / 20))
            main.font_25 = ("Consolas", round(main.res_height / 25))
            main.font_48 = ("Consolas", round(main.res_height / 48))
            main.font_34 = ("Consolas", round(main.res_height / 34))
            main.font_80 = ("Consolas", round(main.res_height / 80))

            LoginMenu.load_page(main.app.frames[LoginMenu])
            self.update_idletasks()  # make page transition less choppy
            main.app.show_frame(LoginMenu)

        # widgets
        tk.Label(self, text="Loading", font=LARGE_FONT, bg=DARK_GREY, fg=ACCENT_COLOUR).pack()
        tk.Button(self, text="Press to continue", font=SMALL_FONT, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: load_main()).pack()
