from PIL import Image, ImageTk
from Queue import Queue
import threading
import Tkinter as tk
import time

from tkintertinkering import safe_print


class TkTinker(tk.Frame):
    def __init__(self, parent, square_size, player_img, dragon_img):
        
        self.rows = 8
        self.columns = 8
        self.square_size = square_size
        self.units = {}
        self.images = {"player": ImageTk.PhotoImage(Image.open(player_img).resize((square_size, square_size),Image.ANTIALIAS)),
                       "dragon": ImageTk.PhotoImage(Image.open(dragon_img).resize((square_size, square_size),Image.ANTIALIAS))}

        self.switch_color = lambda color: "white" if color == "black" else "black"

        canvas_width = self.columns * square_size
        canvas_height = self.rows * square_size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        
        # this binding will cause a refresh if the user interactively changes the window size
        self.canvas.bind("<Configure>", self.refresh)

    def add_units(self, units):
        self.canvas.delete("unit")
        for identifier, image, position in units:
            self.add_unit(identifier, image, position)

    def add_unit(self, identifier, image, position=(0, 0)):
        # Add a piece to the playing board
        self.canvas.create_image(position[0], position[1], image=self.images[image], tags=(identifier, "unit"), anchor="c")
        self.place_unit(identifier, position)

    def place_unit(self, identifier, position):
        # Place a piece at the given row/column
        print self.units
        self.units[identifier] = position
        x0 = (position[1] * self.square_size) + int(self.square_size / 2)
        y0 = (position[0] * self.square_size) + int(self.square_size / 2)
        self.canvas.coords(identifier, x0, y0)

    def refresh(self, event):
        # Redraw the board, possibly in response to window being resized
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("field")
        color = "black"
        for row in range(self.rows):
            color = self.switch_color(color)
            for col in range(self.columns):
                x1 = (col * self.square_size)
                y1 = (row * self.square_size)
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="field")
                color = self.switch_color(color)
        for name in self.units:
            self.place_unit(name, self.units[name])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("field")


class Test(threading.Thread):
    def __init__(self, identifier, queue):
        threading.Thread.__init__(self)
        self.identifier = identifier
        self.board = None
        self.queue = queue

    def run(self):
        safe_print('Hi there, this is {:d}'.format(self.identifier))
        root = tk.Tk()
        board = TkTinker(tk.Toplevel(root), 32, "Superman.png", "Dragon.png")
        board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
        board.add_unit("player1", "player", position=(0, 0))
        self.board = board
        
        while True:
            units = None
            while not self.queue.empty():
                units = self.queue.get()
            if units:
                self.board.add_units(units)
            #board.add_unit("player{:d}".format(i + 2), "player", position=(i % 8, i / 8))
            self.board.canvas.update_idletasks()
            self.board.canvas.update()