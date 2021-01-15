import tkinter as tk
from time import strftime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from PIL import ImageTk, Image
import pandas as pd
from binance_wrapper import get_klines
from indicators import rsi

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
        for F in (Startup, MainMenu, CoinPage):
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
            clock.after(1000, tick)

        tick()

        # graphs
        graph_coins = ["BTC", "ETH", "XRP", "LTC", "LINK", "ADA"]
        graphs_x = [0.05, 0.05, 0.05, 0.1 + (0.8 / 3), 0.1 + (0.8 / 3), 0.1 + (0.8 / 3)]
        graphs_y = [0.25, 0.5, 0.75, 0.25, 0.5, 0.75]  # how much to move each iteration
        percentage_change = [["BTC"], ["ETH"], ["XRP"], ["LTC"], ["LINK"], ["ADA"]]
        for index in range(6):
            df = pd.DataFrame(get_klines(graph_coins[index] + "USDT", "1h", 24),
                              columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                                       "Close time", "Quote asset volume", "Number of trades",
                                       "Taker buy base asset volume",
                                       "Taker buy quote asset volume", "Ignore."])
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
            change = (end_price - start_price) / start_price
            percentage_change[index].append(str(round(change, 2)))

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
            arg = search.get().strip()
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
        gains_font = ("Consolas", round(res_height / 25))
        top_gains = tk.Label(self, text="(%) Change", font=gains_font, bg="#15151c", fg="#3ac7c2")
        top_gains.place(relx=(0.17 + ((0.8 / 3) * 2)), rely=0.27)

        percentage_change.sort(key=lambda x: x[1], reverse=False)
        y = 0.38
        for change in percentage_change:
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

        # settings button
        self.cog_image = ImageTk.PhotoImage(Image.open("images/cog.png")
                                            .resize((rel_width(0.08), rel_height(0.14)), Image.ANTIALIAS))
        settings = tk.Button(self, image=self.cog_image, text="test", bg="#15151c", highlightthickness=0, bd=0,
                             activebackground="#15151c", command=lambda: app.show_frame(CoinPage))
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

        tk.Label(self, text=coin.upper()+" / USDT", font=("Consolas", 40), fg="#67676b", bg="#15151c").pack()

        df = pd.DataFrame(get_klines(coin + "USDT", "1m", 1000),
                          columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                                   "Close time", "Quote asset volume", "Number of trades",
                                   "Taker buy base asset volume",
                                   "Taker buy quote asset volume", "Ignore."])
        figure = plt.Figure(figsize=(0.5 * res_width / 100, 0.8 * res_height / 100), facecolor="#67676b")
        start_price = float(df["Close"][0])
        end_price = float(df["Close"][999])
        if end_price > start_price:
            colour = "g"
        else:
            colour = "r"
        figure.add_subplot(fc="#15151c").plot(df["Close time"], df["Close"].astype(float), "-" + colour)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.1, rely=0.1)


# launch application
app = Application()
app.title("Crypto App")
if platform == "linux":  # change zoom method depending on platform
    app.wm_attributes("-zoomed", 1)
else:
    app.state("zoomed")
app.configure(bg="black")
app.mainloop()
