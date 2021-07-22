import tkinter as tk
from time import strftime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from PIL import ImageTk, Image
from utilities.binance_wrapper import get_klines
import threading
from utilities import indicators, utilities as utils
import json
from utilities.coingecko_wrapper import get_cg
from utilities.lstm import lstm
import hashlib
import sqlite3
import uuid
from tkinter import messagebox

# platform (either linux or win32) for platform specific functions
platform = sys.platform

# variables updates on load
res_width = 1310
res_height = 704
user_id = None

# font and colour variables
LARGE_FONT = ("Consolas", 120)
font_20 = None
font_25 = None
font_28 = None
font_34 = None
font_48 = None
font_80 = None
SMALL_FONT = ("Consolas", 30)

WHITE = "#000000"
DARK_GREY = "#15151c"
ACCENT_COLOUR = "#3ac7c2"
LIGHT_GREY = "#67676b"
BOX_COLOUR = "#1b1b24"


def rel_width(multiplier): return round(multiplier * res_width)


def rel_height(multiplier): return round(multiplier * res_height)


# application class which manages the frame classes
class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # create a container to put all the frames on
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}  # dictionary of frames

        # cycle through frames
        for F in (Startup, LoginMenu, MainMenu, CoinPage, SettingsMenu, AIPage, NewUser):
            frame = F(container)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Startup)  # lift the first frame to the top

    # method to change frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Startup(tk.Frame):  # startup page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.configure(bg=DARK_GREY)  # background colour

        # set the resolution variables and load the login menu
        def load_main():
            global res_width
            res_width = self.winfo_width()
            global res_height
            res_height = self.winfo_height()

            global font_28
            font_28 = ("Consolas", round(res_height / 28))
            global font_20
            font_20 = ("Consolas", round(res_height / 20))
            global font_25
            font_25 = ("Consolas", round(res_height / 25))
            global font_48
            font_48 = ("Consolas", round(res_height / 48))
            global font_34
            font_34 = ("Consolas", round(res_height / 34))
            global font_80
            font_80 = ("Consolas", round(res_height / 80))

            LoginMenu.load_page(app.frames[LoginMenu])
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(LoginMenu)

        # widgets
        tk.Label(self, text="Loading", font=LARGE_FONT, bg=DARK_GREY, fg=ACCENT_COLOUR).pack()
        tk.Button(self, text="Press to continue", font=SMALL_FONT, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: load_main()).pack()


class LoginMenu(tk.Frame):  # login menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=DARK_GREY)

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
                    global user_id
                    user_id = row[0]  # set the user ID
                    print("Login by: " + row[0])
                    MainMenu.load_page(app.frames[MainMenu])  # load the main menu
                    self.update_idletasks()  # make page transition less choppy
                    app.show_frame(MainMenu)
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
        tk.Button(self, text="Add User", font=font_48, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: app.show_frame(NewUser)).place(relx=0.885, rely=0.91)


class NewUser(tk.Frame):  # user creation menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=DARK_GREY)

        # data entries
        tk.Label(self, text="New User", font=font_20, fg=ACCENT_COLOUR, bg=DARK_GREY) \
            .pack(pady=(rel_height(0.45), 0))

        usr = tk.Entry(self, font=font_20, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        usr.pack(pady=(rel_height(0.1), 0))

        pwd = tk.Entry(self, font=font_20, bg=DARK_GREY, fg=ACCENT_COLOUR,
                       highlightbackground=LIGHT_GREY)
        pwd.pack(pady=(2, 0))

        def create_user():
            passwd = hashlib.sha256(pwd.get().encode('utf-8')).hexdigest()  # hash the password entry
            conn = sqlite3.connect("data/logins.db")
            c = conn.cursor()
            new_uuid = str(uuid.uuid1())
            c.execute("INSERT INTO logins VALUES (?, ?, ?)", (new_uuid, usr.get(), passwd))  # write to the database
            c.execute('SELECT * FROM logins')
            conn.commit()
            conn.close()
            app.show_frame(LoginMenu)  # go back to the login menu

            with open("data/settings.json", "r") as settings_file:  # create a default settings profile for the new user
                settings = json.load(settings_file)  # get settings
                settings.append({"uuid": new_uuid, "favourites": ["BTC", "ETH", "XRP", "LTC", "LINK", "ADA"]})  # add
            with open("data/settings.json", "w") as settings_file:
                json.dump(settings, settings_file, indent=4)  # write new settings

        tk.Button(self, text="Create", font=font_20, bg=DARK_GREY, fg=LIGHT_GREY,
                  command=lambda: create_user()).pack(pady=(rel_height(0.1), 0))


class MainMenu(tk.Frame):  # main menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.cog_image = None  # make variable for image else it will be garbage collected
        self.configure(bg=DARK_GREY)

    def load_page(self):
        # blank canvas for drawing shapes
        canvas = tk.Canvas(self, width=res_width, height=res_height, bg=DARK_GREY, highlightbackground=DARK_GREY)
        canvas.pack()

        # working clock
        clock = tk.Label(self, font=font_28, bg=DARK_GREY, fg=LIGHT_GREY)
        clock.place(relx=0.8, rely=0.08)

        def tick():
            clock.config(text=strftime("%H:%M:%S"))  # set to current time
            clock.after(500, tick)  # repeat every half second

        tick()

        def graph_drawing():
            # graphs
            graphs_x = [0.05, 0.05, 0.05, 0.1 + (0.8 / 3), 0.1 + (0.8 / 3), 0.1 + (0.8 / 3)]
            graphs_y = [0.235, 0.4875, 0.74, 0.235, 0.4875, 0.74]  # where to place each iteration
            with open("data/settings.json", "r") as settings_file:
                profiles = json.load(settings_file)
                for profile in profiles:  # search profiles for the current users preferences
                    if profile["uuid"] == user_id:
                        fav_coins = [[fav] for fav in profile["favourites"]]  # nested array for values

            for index in range(6):
                df = get_klines(fav_coins[index][0] + "USDT", 1, "h", 24)  # retrieve the candlestick data
                figure = plt.Figure(figsize=(0.3 * res_width / 100, 0.26 * res_height / 100), facecolor=DARK_GREY)
                start_price = float(df["Close"][0])
                end_price = float(df["Close"][23])
                if end_price > start_price:
                    colour = "g"  # green if positive change
                else:
                    colour = "r"  # red otherwise

                # styling
                ax = figure.add_subplot(111, fc=DARK_GREY)
                ax.set_xlabel("Time (hrs)", fontsize=round(res_height / 80))
                ax.set_ylabel("Value ($)", fontsize=round(res_height / 80))
                ax.xaxis.label.set_color(LIGHT_GREY)
                ax.yaxis.label.set_color(LIGHT_GREY)
                for axis in ["bottom", "left"]:  # modify borders
                    ax.spines[axis].set_color(LIGHT_GREY)
                    ax.spines[axis].set_linewidth(3)
                for axis in ["top", "right"]:  # remove borders
                    ax.spines[axis].set_linewidth(0)
                for axis in ["x", "y"]:
                    ax.tick_params(axis=axis, colors=LIGHT_GREY, which="both", width=2)
                figure.tight_layout()
                figure.subplots_adjust(left=0.11)

                ax.plot([i * -1 for i in range(0, 24)][::-1], df["Close"].astype(float), "-" + colour)  # over -24hr
                FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=graphs_x[index], rely=graphs_y[index])

                tk.Label(self, text=str(fav_coins[index][0]).upper(), font=font_80, bg=BOX_COLOUR, fg=ACCENT_COLOUR) \
                    .place(relx=graphs_x[index] + 0.26, rely=graphs_y[index] + 0.03)

                # percentage change
                change = ((end_price - start_price) / start_price) * 100
                fav_coins[index].append(str(round(change, 2)))

            # coin list on right
            fav_coins.sort(key=lambda x: float(x[1]), reverse=True)  # sort by percentage change
            y = 0.38
            for change in fav_coins:
                if float(change[1]) > 0:
                    symbol = "+"  # add symbol if positive
                else:
                    symbol = ""
                name = change[0]  # for equal spacing
                while len(name) < 4:
                    name += " "  # add a space until 4 characters long
                tk.Label(self, text=f"{name} | {symbol}{change[1]}%", font=font_25, bg=DARK_GREY, fg=LIGHT_GREY) \
                    .place(relx=(0.165 + ((0.8 / 3) * 2)), rely=y)
                y += 0.09

        threading.Thread(target=graph_drawing).start()  # start in new thread to prevent app freeze

        # search bar
        search = tk.Entry(self, font=font_28, bg=DARK_GREY, fg=ACCENT_COLOUR,
                          highlightbackground=LIGHT_GREY)
        search.insert(0, " Search")

        def clear_search(event):  # clear the search bar when left click
            search.insert(0, " ")
            search.delete(1, tk.END)

        search.bind("<Button-1>", clear_search)
        search.place(relx=0.35, rely=0.06, width=0.3 * res_width, height=0.1 * res_height)

        def initiate_search(event):  # load the coin page with the entered coin
            arg = search.get().replace(" ", "").upper()
            CoinPage.load_page(app.frames[CoinPage], arg)
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(CoinPage)

        search.bind("<Return>", initiate_search)  # search when enter is pressed

        # grid on right hand side
        canvas.create_rectangle(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.25 * res_height),
                                round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.95 * res_height),
                                width=5, outline=LIGHT_GREY)
        canvas.create_line(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.35 * res_height),
                           round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.35 * res_height),
                           width=5, fill=LIGHT_GREY)
        top_gains = tk.Label(self, text="(%) Change", font=font_25, bg=DARK_GREY, fg=ACCENT_COLOUR)
        top_gains.place(relx=(0.17 + ((0.8 / 3) * 2)), rely=0.27)

        # settings button
        def open_settings():
            SettingsMenu.load_page(app.frames[SettingsMenu])
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(SettingsMenu)

        self.cog_image = ImageTk.PhotoImage(Image.open("images/cog.png")
                                            .resize((rel_width(0.075), rel_height(0.14)), Image.ANTIALIAS))
        settings = tk.Button(self, image=self.cog_image, text="test", bg=DARK_GREY, highlightthickness=0, bd=0,
                             activebackground=DARK_GREY, command=lambda: open_settings())
        settings.place(relx=0.06, rely=0.05, width=rel_width(0.08), height=rel_height(0.14))


class CoinPage(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def load_page(self, coin):
        self.configure(bg=DARK_GREY)

        def clear_page(event):  # wipe the page
            for child in self.winfo_children():
                child.destroy()  # destroy all widgets
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)  # return to main menu with escape key

        tk.Label(self, text=coin + " / USDT", font=font_48, fg=LIGHT_GREY, bg=DARK_GREY) \
            .pack(pady=rel_height(0.01))

        def draw_graph():
            df = get_klines(coin + "USDT", 1, "m", 1440)  # retrieve the past 24 hrs in 1 minute intervals
            reverse_time = [i * -1 for i in range(0, 1440)][::-1]

            # volume graph first (for overlap)
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.2 * res_height / 100), facecolor=DARK_GREY)

            ax = figure.add_subplot(111, fc=DARK_GREY)
            ax.set_ylabel("Volume ($)", fontsize=round(res_height / 80))
            ax.xaxis.label.set_color(LIGHT_GREY)
            ax.yaxis.label.set_color(LIGHT_GREY)
            for axis in ["left"]:  # modify borders
                ax.spines[axis].set_color(LIGHT_GREY)
                ax.spines[axis].set_linewidth(3)
            for axis in ["top", "right", "bottom"]:  # remove borders
                ax.spines[axis].set_linewidth(0)
            for axis in ["x", "y"]:
                ax.tick_params(axis=axis, colors=LIGHT_GREY, which="both", width=2)
            figure.subplots_adjust(left=0.1, right=1.0, bottom=0.0, top=1.0)

            ax.plot(reverse_time, df["Volume"].astype(float), "-w")
            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.06)

            # same methods as main menu graph production
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.45 * res_height / 100), facecolor=DARK_GREY)
            start_price = float(df["Close"][0])
            end_price = float(df["Close"][1439])
            if end_price > start_price:
                colour = "g"
            else:
                colour = "r"

            ax = figure.add_subplot(111, fc=DARK_GREY)
            ax.set_ylabel("Price ($)", fontsize=round(res_height / 80))
            ax.xaxis.label.set_color(LIGHT_GREY)
            ax.yaxis.label.set_color(LIGHT_GREY)
            for axis in ["left"]:  # modify borders
                ax.spines[axis].set_color(LIGHT_GREY)
                ax.spines[axis].set_linewidth(3)
            for axis in ["top", "right", "bottom"]:  # remove borders
                ax.spines[axis].set_linewidth(0)
            for axis in ["x", "y"]:
                ax.tick_params(axis=axis, colors=LIGHT_GREY, which="both", width=2)
            figure.subplots_adjust(left=0.1, right=1.0, bottom=0.0, top=1.0)

            ax.plot(reverse_time, df["Close"].astype(float), "-" + colour)  # plot main line

            # moving average
            moving_avg = indicators.moving_avg(df)
            ax.plot(reverse_time, moving_avg, "-", color=(1.0, 1.0, 1.0, 0.3))  # plot ma

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.27)

            # relative strength index 1
            rsi_df1 = indicators.rsi(df, 14)
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.25 * res_height / 100), facecolor=DARK_GREY)

            # styling
            ax = figure.add_subplot(111, fc=DARK_GREY)
            ax.set_xlabel("Time (minutes)", fontsize=round(res_height / 80))
            ax.set_ylabel("RSI (%)", fontsize=round(res_height / 80))
            ax.xaxis.label.set_color(LIGHT_GREY)
            ax.yaxis.label.set_color(LIGHT_GREY)
            for axis in ["bottom", "left"]:  # modify borders
                ax.spines[axis].set_color(LIGHT_GREY)
                ax.spines[axis].set_linewidth(3)
            for axis in ["top", "right"]:  # remove borders
                ax.spines[axis].set_linewidth(0)
            for axis in ["x", "y"]:
                ax.tick_params(axis=axis, colors=LIGHT_GREY, which="both", width=2)
            figure.subplots_adjust(left=0.1, right=1.0, bottom=0.15, top=1.0)

            ax.plot(reverse_time, rsi_df1.tolist(), "-", color="#2bc2d6")

            # relative strength index 2
            rsi_df2 = indicators.rsi(df, 28)
            ax.plot(reverse_time, rsi_df2.tolist(), "-", color="#dd54a2")

            # relative strength index 3
            rsi_df3 = indicators.rsi(df, 56)
            ax.plot(reverse_time, rsi_df3.tolist(), "-", color="#7a72ad")

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.73)

            # right hand side stats

            # current price
            tk.Label(self, text="Price Now: $" + "{:,.2f}".format(end_price), font=font_34,
                     bg=DARK_GREY, fg=ACCENT_COLOUR).place(relx=0.73, rely=0.1)

            # 24 hour high
            day_high = round(float(df["Close"].max()), 2)
            tk.Label(self, text="24hr High: $" + "{:,.2f}".format(day_high), font=font_34,
                     bg=DARK_GREY, fg=ACCENT_COLOUR).place(relx=0.73, rely=0.18)

            # 24 hour low
            day_low = round(float(df["Close"].min()), 2)
            tk.Label(self, text="24hr Low: $" + "{:,.2f}".format(day_low), font=font_34,
                     bg=DARK_GREY, fg=ACCENT_COLOUR).place(relx=0.73, rely=0.26)

            # 24 hour percentage change
            per_change = round(((end_price - start_price) / start_price) * 100, 2)
            per_change = "+" + str(per_change) if per_change > 0 else "" + str(per_change)
            tk.Label(self, text="24hr Change: " + per_change + "%", font=font_34, bg=DARK_GREY, fg=ACCENT_COLOUR) \
                .place(relx=0.73, rely=0.34)

            # relative strength index 1
            current_rsi1 = round(rsi_df1.iloc[-1], 4)
            tk.Label(self, text="14m RSI: " + str(current_rsi1), font=font_34, bg=DARK_GREY, fg=ACCENT_COLOUR) \
                .place(relx=0.73, rely=0.42)

            # relative strength index 2
            current_rsi2 = round(rsi_df2.iloc[-1], 4)
            tk.Label(self, text="28m RSI: " + str(current_rsi2), font=font_34, bg=DARK_GREY, fg=ACCENT_COLOUR) \
                .place(relx=0.73, rely=0.50)

            # relative strength index 3
            current_rsi3 = round(rsi_df3.iloc[-1], 4)
            tk.Label(self, text="56m RSI: " + str(current_rsi3), font=font_34, bg=DARK_GREY, fg=ACCENT_COLOUR) \
                .place(relx=0.73, rely=0.58)

            def run_ai(dataframe):  # execute ai separately so not demanding on hardware when unwanted
                AIPage.load_page(app.frames[AIPage], dataframe)
                self.update_idletasks()  # make page transition less choppy
                app.show_frame(AIPage)

            tk.Button(self, text="Initiate AI", bg=DARK_GREY, highlightthickness=0, bd=2,
                      highlightbackground=LIGHT_GREY,
                      font=font_34, activebackground=DARK_GREY, fg=LIGHT_GREY,
                      command=lambda: run_ai(df)).place(relx=0.78, rely=0.90)

        threading.Thread(target=draw_graph).start()  # run on new thread

        def coin_gecko_stats():  # stats from CoinGecko.com
            cg_id = None
            with open("data/cg_coins.json", "r") as cg_file:
                cg_ids = json.load(cg_file)
                for item in cg_ids:
                    if item["symbol"].upper() == coin:
                        cg_id = item["id"]  # retrieve the CoinGecko id from cg_coins.json with the symbol

            if cg_id is None:
                return  # exit if no coin is found (results in empty page instead of crash)
            cg_data = get_cg(cg_id)

            # market cap
            market_cap = cg_data["market_data"]["market_cap"]["usd"]
            tk.Label(self, text="Market Cap: $" + utils.number_suffix(market_cap), font=font_34,
                     bg=DARK_GREY, fg=ACCENT_COLOUR).place(relx=0.73, rely=0.66)

            # 24hr trade volume
            volume = cg_data["market_data"]["total_volume"]["usd"]
            tk.Label(self, text="Trade Volume: $" + utils.number_suffix(volume), font=font_34, bg=DARK_GREY,
                     fg=ACCENT_COLOUR).place(relx=0.73, rely=0.74)

            # all time high
            ath = cg_data["market_data"]["ath"]["usd"]
            tk.Label(self, text="All-Time Hi: $" + "{:,.2f}".format(ath), font=font_34, bg=DARK_GREY,
                     fg=ACCENT_COLOUR).place(relx=0.73, rely=0.82)

        threading.Thread(target=coin_gecko_stats).start()  # start on new thread


class SettingsMenu(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=DARK_GREY)

    def load_page(self):
        def clear_page(event):  # wipe the page
            for child in self.winfo_children():
                child.destroy()  # destroy all widgets
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)

        editor = tk.Text(self, bg=BOX_COLOUR, fg=LIGHT_GREY, highlightbackground=WHITE,
                         height=6, font=font_25)
        editor.pack()

        with open("data/settings.json", "r") as settings_file:
            profiles = json.load(settings_file)
            for profile in profiles:
                if profile["uuid"] == user_id:  # identify the user by their ID
                    for fav in profile["favourites"]:
                        editor.insert(tk.END, fav + "\n")  # load the preferences and each coin on a new line

        # save button and function
        def save_settings():
            modification = list(editor.get("1.0", "end-1c").splitlines())  # add values to a list
            profile["favourites"] = modification
            with open("data/settings.json", "w") as settings_file2:  # write the profile back to the settings file
                json.dump(profiles, settings_file2, indent=4)

        save_button = tk.Button(self, command=lambda: save_settings(), font=font_20,
                                text="Save", bg=BOX_COLOUR, fg=ACCENT_COLOUR, highlightbackground=WHITE)
        save_button.pack()


class AIPage(tk.Frame):  # machine learning page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=DARK_GREY)

    def load_page(self, df):
        def clear_page(event):  # wipe the page
            for child in self.winfo_children():
                child.destroy()  # destroy all widgets
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)

        def draw_graph():  # standard graph drawing method with additional data
            figure = plt.Figure(figsize=(1.0 * res_width / 100, 1.0 * res_height / 100), facecolor=DARK_GREY)

            # styling
            ax = figure.add_subplot(111, fc=DARK_GREY)
            ax.set_xlabel("Time (minutes)", fontsize=round(res_height / 80))
            ax.set_ylabel("RSI (%)", fontsize=round(res_height / 80))
            ax.xaxis.label.set_color(LIGHT_GREY)
            ax.yaxis.label.set_color(LIGHT_GREY)
            for axis in ["bottom", "left"]:  # modify borders
                ax.spines[axis].set_color(LIGHT_GREY)
                ax.spines[axis].set_linewidth(3)
            for axis in ["top", "right"]:  # remove borders
                ax.spines[axis].set_linewidth(0)
            for axis in ["x", "y"]:
                ax.tick_params(axis=axis, colors=LIGHT_GREY, which="both", width=2)
            figure.subplots_adjust(left=0.1, right=1.0, bottom=0.15, top=1.0)
            figure.tight_layout()

            ax.plot(df["Close time"], df["Close"].astype(float), "-b")

            # loading text covered by graph
            loading_bar = ""  #TODO dont work
            tk.Label(self, text=f"{loading_bar}", font=LARGE_FONT, bg=DARK_GREY, fg=ACCENT_COLOUR) \
                .place(relx=0.5, rely=0.5, anchor="center")

            # lstm
            lstm_res = lstm(df["Close"].astype(float).tolist(), 100)
            lstm_time = [df["Close time"].iloc[-1] + 60000]
            for i in range(99):
                lstm_time.append(lstm_time[-1] + 60000)
                loading_bar += "▇"
                app.update_idletasks()
            ax.plot(lstm_time, lstm_res, "-w")  # add the machine learnt data on top

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(x=0, y=0)

        threading.Thread(target=draw_graph).start()  # start in a new thread


# launch application
app = Application()
app.title("Crypto App")
if platform == "linux":  # change zoom method depending on platform
    app.wm_attributes("-zoomed", 1)
else:  # windows
    app.state("zoomed")
    app.iconbitmap("images/icon.ico")
app.configure(bg="black")
app.mainloop()
