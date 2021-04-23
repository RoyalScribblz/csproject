import tkinter as tk
from time import strftime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from PIL import ImageTk, Image
from binance_wrapper import get_klines
import threading
import indicators
import json
from coingecko_wrapper import get_cg
import utilities as utils
from lstm import lstm

# current directory and platform (either linux or win32)
cdir = os.getcwd()
platform = sys.platform

# variable updates on load
res_width = 1310
res_height = 704


def rel_width(multiplier): return round(multiplier * res_width)


def rel_height(multiplier): return round(multiplier * res_height)


# app class
class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        # cycle through windows
        for F in (Startup, MainMenu, CoinPage, SettingsMenu, AIPage):
            frame = F(container)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Startup)

    # method to change frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Startup(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.configure(bg="#15151c")

        def load_main():
            global res_width
            res_width = self.winfo_width()
            global res_height
            res_height = self.winfo_height()

            MainMenu.load_page(app.frames[MainMenu])
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(MainMenu)

        tk.Label(self, text="Loading", font=("Consolas", 120), bg="#15151c", fg="#3ac7c2").pack()
        tk.Button(self, text="Press to continue", font=("Consolas", 40), bg="#15151c", fg="#67676b",
                  command=lambda: load_main()).pack()


class MainMenu(tk.Frame):  # main menu
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.cog_image = None
        self.configure(bg="#15151c")

    def load_page(self):
        # blank canvas for drawing shapes
        canvas = tk.Canvas(self, width=res_width, height=res_height, bg="#15151c", highlightbackground="#15151c")
        canvas.pack()

        # working clock
        clock_font = ("Consolas", rel_height(0.04))
        clock = tk.Label(self, font=clock_font, bg="#15151c", fg="#67676b")
        clock.place(relx=0.8, rely=0.08)

        def tick():
            clock.config(text=strftime("%H:%M:%S"))
            clock.after(500, tick)

        tick()

        gains_font = ("Consolas", round(res_height / 25))

        def graph_drawing():
            # graphs
            graphs_x = [0.05, 0.05, 0.05, 0.1 + (0.8 / 3), 0.1 + (0.8 / 3), 0.1 + (0.8 / 3)]
            graphs_y = [0.25, 0.5, 0.75, 0.25, 0.5, 0.75]  # how much to move each iteration
            with open("settings.json", "r") as settings_file:
                faves = json.load(settings_file)["favourites"]
                fav_coins = [[fav] for fav in faves]
            for index in range(6):

                df = get_klines(fav_coins[index][0] + "USDT", 1, "h", 24)
                figure = plt.Figure(figsize=((0.8 / 3) * res_width / 100, 0.2 * res_height / 100), facecolor="#67676b")
                start_price = float(df["Close"][0])
                end_price = float(df["Close"][23])
                if end_price > start_price:
                    colour = "g"
                else:
                    colour = "r"
                figure.add_subplot(fc="#15151c").plot(df["Close time"], df["Close"].astype(float), "-" + colour)
                FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=graphs_x[index], rely=graphs_y[index])

                # percentage change
                change = ((end_price - start_price) / start_price) * 100
                fav_coins[index].append(str(round(change, 2)))

            # coin list on right
            fav_coins.sort(key=lambda x: float(x[1]), reverse=True)
            y = 0.38
            for change in fav_coins:
                if float(change[1]) > 0:
                    symbol = "+"
                else:
                    symbol = ""
                name = change[0]  # for equal spacing
                while len(name) < 4:
                    name += " "  # add a space until 4 characters long
                tk.Label(self, text=f"{name} | {symbol}{change[1]}%", font=gains_font, bg="#15151c", fg="#67676b") \
                    .place(relx=(0.165 + ((0.8 / 3) * 2)), rely=y)
                y += 0.09

        threading.Thread(target=graph_drawing).start()

        # search bar
        search = tk.Entry(self, font=("Consolas", round(res_height / 28)), bg="#15151c", fg="#3ac7c2",
                          highlightbackground="#67676b")
        search.insert(0, " Search")

        def clear_search(event):
            search.insert(0, " ")
            search.delete(1, tk.END)

        search.bind("<Button-1>", clear_search)
        search.place(relx=0.35, rely=0.06, width=0.3 * res_width, height=0.1 * res_height)

        def initiate_search(event):
            arg = search.get().strip().upper()
            CoinPage.load_page(app.frames[CoinPage], arg)
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(CoinPage)

        search.bind("<Return>", initiate_search)

        # grid on right
        canvas.create_rectangle(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.25 * res_height),
                                round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.95 * res_height),
                                width=5, outline="#67676b")
        canvas.create_line(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.35 * res_height),
                           round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.35 * res_height),
                           width=5, fill="#67676b")
        top_gains = tk.Label(self, text="(%) Change", font=gains_font, bg="#15151c", fg="#3ac7c2")
        top_gains.place(relx=(0.17 + ((0.8 / 3) * 2)), rely=0.27)

        # settings button
        def open_settings():
            SettingsMenu.load_page(app.frames[SettingsMenu])
            self.update_idletasks()  # make page transition less choppy
            app.show_frame(SettingsMenu)

        self.cog_image = ImageTk.PhotoImage(Image.open("images/cog.png")
                                            .resize((rel_width(0.08), rel_height(0.14)), Image.ANTIALIAS))
        settings = tk.Button(self, image=self.cog_image, text="test", bg="#15151c", highlightthickness=0, bd=0,
                             activebackground="#15151c", command=lambda: open_settings())
        settings.place(relx=0.06, rely=0.05, width=rel_width(0.08), height=rel_height(0.14))


class CoinPage(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def load_page(self, coin):
        self.configure(bg="#15151c")

        def clear_page(event):
            for child in self.winfo_children():
                child.destroy()
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)

        tk.Label(self, text=coin + " / USDT", font=("Consolas", round(res_height / 48)), fg="#67676b", bg="#15151c") \
            .pack(pady=rel_height(0.01))

        stats_font = ("Consolas", round(res_height / 34))

        def draw_graph():
            df = get_klines(coin + "USDT", 1, "m", 1440)

            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.65 * res_height / 100), facecolor="#67676b")
            start_price = float(df["Close"][0])
            end_price = float(df["Close"][1439])
            if end_price > start_price:
                colour = "g"
            else:
                colour = "r"
            figure.add_subplot(fc="#15151c").plot(df["Close time"], df["Close"].astype(float), "-" + colour)

            # moving average
            moving_avg = indicators.moving_avg(df)
            figure.add_subplot(fc="#15151c").plot(df["Close time"], moving_avg, "-w")

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.2)

            # relative strength index
            rsi_df1 = indicators.rsi(df, 14)
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.2 * res_height / 100), facecolor="#67676b")
            figure.add_subplot(fc="#15151c").plot(df["Close time"], rsi_df1.tolist(), "-b")

            # relative strength index
            rsi_df2 = indicators.rsi(df, 28)
            figure.add_subplot(fc="#15151c").plot(df["Close time"], rsi_df2.tolist(), "-m")

            # relative strength index
            rsi_df3 = indicators.rsi(df, 56)
            figure.add_subplot(fc="#15151c").plot(df["Close time"], rsi_df3.tolist(), "-y")

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.8)

            # volume graph
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.2 * res_height / 100), facecolor="#67676b")
            figure.add_subplot(fc="#15151c").plot(df["Close time"], df["Volume"].astype(float), "-w")
            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.06)

            # right hand side stats

            tk.Label(self, text="Price Now: $" + "{:,.2f}".format(end_price), font=stats_font,
                     bg="#15151c", fg="#3ac7c2").place(relx=0.73, rely=0.1)

            day_high = round(float(df["Close"].max()), 2)
            tk.Label(self, text="24hr High: $" + "{:,.2f}".format(day_high), font=stats_font,
                     bg="#15151c", fg="#3ac7c2").place(relx=0.73, rely=0.18)

            day_low = round(float(df["Close"].min()), 2)
            tk.Label(self, text="24hr Low: $" + "{:,.2f}".format(day_low), font=stats_font,
                     bg="#15151c", fg="#3ac7c2").place(relx=0.73, rely=0.26)

            per_change = round(((end_price - start_price) / start_price) * 100, 2)
            per_change = "+" + str(per_change) if per_change > 0 else "" + str(per_change)
            tk.Label(self, text="24hr Change: " + per_change + "%", font=stats_font, bg="#15151c", fg="#3ac7c2") \
                .place(relx=0.73, rely=0.34)

            current_rsi1 = round(rsi_df1.iloc[-1], 4)
            tk.Label(self, text="14m RSI: " + str(current_rsi1), font=stats_font, bg="#15151c", fg="#3ac7c2") \
                .place(relx=0.73, rely=0.42)

            current_rsi2 = round(rsi_df2.iloc[-1], 4)
            tk.Label(self, text="28m RSI: " + str(current_rsi2), font=stats_font, bg="#15151c", fg="#3ac7c2") \
                .place(relx=0.73, rely=0.50)

            current_rsi3 = round(rsi_df3.iloc[-1], 4)
            tk.Label(self, text="56m RSI: " + str(current_rsi3), font=stats_font, bg="#15151c", fg="#3ac7c2") \
                .place(relx=0.73, rely=0.58)

            def run_ai(dataframe):
                AIPage.load_page(app.frames[AIPage], dataframe)
                self.update_idletasks()  # make page transition less choppy
                app.show_frame(AIPage)
            tk.Button(self, text="Initiate AI", bg="#15151c", highlightthickness=0, bd=2, highlightbackground="#67676b",
                      font=("Consolas", round(res_height / 34)), activebackground="#15151c", fg="#67676b",
                      command=lambda: run_ai(df)).place(relx=0.78, rely=0.90)

        threading.Thread(target=draw_graph).start()

        def coin_gecko_stats():
            cg_id = None
            with open("cg_coins.json", "r") as cg_file:
                cg_ids = json.load(cg_file)
                for item in cg_ids:
                    if item["symbol"].upper() == coin:
                        cg_id = item["id"]

            if cg_id is None:
                return
            cg_data = get_cg(cg_id)

            market_cap = cg_data["market_data"]["market_cap"]["usd"]
            tk.Label(self, text="Market Cap: $" + utils.number_suffix(market_cap), font=stats_font,
                     bg="#15151c", fg="#3ac7c2").place(relx=0.73, rely=0.66)

            volume = cg_data["market_data"]["total_volume"]["usd"]
            tk.Label(self, text="Trade Volume: $" + utils.number_suffix(volume), font=stats_font, bg="#15151c",
                     fg="#3ac7c2").place(relx=0.73, rely=0.74)

            ath = cg_data["market_data"]["ath"]["usd"]
            tk.Label(self, text="All-Time Hi: $" + "{:,.2f}".format(ath), font=stats_font, bg="#15151c",
                     fg="#3ac7c2").place(relx=0.73, rely=0.82)
        threading.Thread(target=coin_gecko_stats).start()


class SettingsMenu(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#15151c")

    def load_page(self):
        def clear_page(event):
            for child in self.winfo_children():
                child.destroy()
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)

        editor = tk.Text(self, bg="#1b1b24", fg="#838391", highlightbackground="#000000",
                         height=6, font=("Consolas", 50))
        editor.pack()
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
            for fav in settings["favourites"]:
                editor.insert(tk.END, fav + "\n")

        def save_settings():
            modification = list(editor.get("1.0", "end-1c").splitlines())
            settings["favourites"] = modification
            with open("settings.json", "w") as settings_file2:
                json.dump(settings, settings_file2)

        save_button = tk.Button(self, command=lambda: save_settings(),
                                text="Save", bg="#1b1b24", fg="#3ac7c2", highlightbackground="#000000")
        save_button.pack()


class AIPage(tk.Frame):  # second page
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#15151c")

    def load_page(self, df):
        def clear_page(event):
            for child in self.winfo_children():
                child.destroy()
            app.show_frame(MainMenu)

        app.bind("<Escape>", clear_page)

        def draw_graph():
            figure = plt.Figure(figsize=(0.7 * res_width / 100, 0.65 * res_height / 100), facecolor="#67676b")
            figure.add_subplot(fc="#15151c").plot(df["Close time"], df["Close"].astype(float), "-b")

            # lstm
            lstm_res = lstm(df["Close"].astype(float).tolist(), 50)
            lstm_time = [df["Close time"].iloc[-1] + 60000]
            for i in range(49):
                lstm_time.append(lstm_time[-1] + 60000)
            print(lstm_time)
            print(lstm_res)
            figure.add_subplot(fc="#15151c").plot(lstm_time, lstm_res, "-w")

            FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.02, rely=0.2)
        threading.Thread(target=draw_graph).start()


# launch application
app = Application()
app.title("Crypto App")
if platform == "linux":  # change zoom method depending on platform
    app.wm_attributes("-zoomed", 1)
else:
    app.state("zoomed")
app.configure(bg="black")
app.mainloop()
