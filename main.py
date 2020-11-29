import tkinter as tk
from time import strftime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from PIL import ImageTk, Image

cdir = os.getcwd()

res_width = 1310
res_height = 704


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (MainMenu, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainMenu)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainMenu(tk.Frame):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)

        canvas = tk.Canvas(self, width=res_width, height=res_height, bg="#15151c", highlightbackground="#15151c")
        canvas.pack()

        # clock
        clock_font = ("Consolas", round(res_height / 25))
        clock = tk.Label(self, font=clock_font, bg="#15151c", fg="#67676b")
        clock.place(relx=0.85, rely=0.07)

        def tick():
            clock.config(text=strftime("%H:%M:%S"))
            clock.after(1000, tick)

        tick()

        figure = plt.Figure(figsize=((0.8 / 3) * res_width / 100, 0.2 * res_height / 100), facecolor="#67676b")
        figure.add_subplot(111, fc="#15151c").plot([1, 2, 3, 4], [1, 5, 7, 6], ".-g")
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.05, rely=0.25)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.05, rely=0.5)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.05, rely=0.75)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.1 + (0.8 / 3), rely=0.25)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.1 + (0.8 / 3), rely=0.5)
        FigureCanvasTkAgg(figure, self).get_tk_widget().place(relx=0.1 + (0.8 / 3), rely=0.75)

        search = tk.Entry(font=("Consolas", round(res_height / 28)), bg="#15151c", fg="#3ac7c2",
                          highlightbackground="#67676b")
        search.insert(0, " Search")
        search.place(relx=0.35, rely=0.06, width=0.3 * res_width, height=0.1 * res_height)

        canvas.create_rectangle(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.25 * res_height),
                                round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.95 * res_height),
                                width=5, outline="#67676b")
        canvas.create_line(round((0.15 + ((0.8 / 3) * 2)) * res_width), round(0.35 * res_height),
                           round((0.15 + ((0.8 / 3) * 3)) * res_width), round(0.35 * res_height),
                           width=5, fill="#67676b")
        gains_font = ("Consolas", round(res_height / 25))
        top_gains = tk.Label(self, text="Top Gains", font=gains_font, bg="#15151c", fg="#3ac7c2")
        top_gains.place(relx=(0.17 + ((0.8 / 3) * 2)), rely=0.27)

        canvas.create_oval(0.05*res_width, 0.05*res_height, 0.15*res_width, 0.15*res_height, fill="#67676b",
                           outline="#3ac7c2")

        cog_image = ImageTk.PhotoImage(Image.open("images/cog.png"))
        settings = tk.Button(image=cog_image, text="test")
        settings.place(relx=0.05, rely=0.05, width=100, height=100)


class PageTwo(tk.Frame):
    def __init__(self, parent, app):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="pg2", font=("Consolas", 40)).pack()


app = Application()
app.title("Crypto App")
app.wm_attributes("-zoomed", 1)
app.configure(bg="black")
app.mainloop()
