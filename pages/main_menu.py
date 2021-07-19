import main
import tkinter as tk
from main import DARK_GREY, res_width, res_height, font_28, LIGHT_GREY, user_id, font_80, ACCENT_COLOUR, BOX_COLOUR
from time import strftime
from utilities.binance_wrapper import get_klines


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