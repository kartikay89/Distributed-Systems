from PIL import Image, ImageTk
import Tkinter as tk

from networking import Dragon, Player


class DASBoard(tk.Frame):
    def __init__(self, parent, square_size, player_img, dragon_img, board_size):
        self.rows, self.columns = board_size
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

    def update_units(self, units):
        self.canvas.delete("unit")
        for unit in units:
            if type(unit) == Player:
                self.add_unit(unit.player, self.images["player"], unit.field.position)
            else:
                self.add_unit(unit.identifier, self.images["dragon"], unit.field.position)

    def add_unit(self, identifier, image, position=(0, 0)):
        # Add a piece to the playing board
        self.canvas.create_image(position[0], position[1], image=image, tags=(identifier, "unit"), anchor="c")
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
        previous_row = "white"
        for row in range(self.rows):
            color = self.switch_color(previous_row)
            previous_row = color
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