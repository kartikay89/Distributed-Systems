# Based on https://github.com/liudmil-mitev/Simple-Python-Chess

from PIL import Image, ImageTk
import Tkinter as tk

from networking import Dragon, GameAction, GameActionType, Message, MessageType, Player, \
                       safe_print


class DASBoard(tk.Frame):
    def __init__(self, parent, square_size, player_img, dragon_img, board_size, message_queue=None):
        self.rows, self.columns = board_size
        self.square_xsize = self.square_ysize = square_size
        self.square_size = min(self.square_xsize, self.square_ysize)
        self.unit_objects = None
        self.units = {}
        self.image_names = {'player': player_img, 'dragon': dragon_img}
        self.images = {}
        self.update_images()
        self.message_queue = message_queue

        self.switch_color = lambda color: 'white' if color == 'black' else 'black'

        canvas_width = self.columns * square_size
        canvas_height = self.rows * square_size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background='bisque')
        self.canvas.pack(side='top', fill='both', expand=True, padx=2, pady=2)
        
        # this binding will cause a refresh if the user interactively changes the window size
        self.canvas.bind('<Configure>', self.refresh)
        self.canvas.bind('<Button-1>', self.click_handler)

    def update_images(self):
        original_player = Image.open(self.image_names['player'])
        self.images['player'] = ImageTk.PhotoImage(original_player.resize((self.square_xsize, self.square_ysize), Image.ANTIALIAS))
        original_dragon = Image.open(self.image_names['dragon'])
        self.images['dragon'] = ImageTk.PhotoImage(original_dragon.resize((self.square_xsize, self.square_ysize), Image.ANTIALIAS))

    def update_units(self, units):
        self.canvas.delete('unit')
        self.unit_objects = units
        if units:
            for unit in units:
                if type(unit) == Player:
                    self.add_unit(unit.player, self.images['player'], unit.field.position)
                else:
                    self.add_unit(unit.identifier, self.images['dragon'], unit.field.position)

    def add_unit(self, identifier, image, position=(0, 0)):
        # Add a piece to the playing board
        self.canvas.create_image(position[0], position[1], image=image, tags=(identifier, 'unit'), anchor='c')
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
        self.square_xsize = int((event.width-1) / self.columns)
        self.square_ysize = int((event.height-1) / self.rows)
        self.square_size = min(self.square_xsize, self.square_ysize)
        self.canvas.delete('field')
        previous_row = 'white'
        for row in range(self.rows):
            color = self.switch_color(previous_row)
            previous_row = color
            for col in range(self.columns):
                x1 = (col * self.square_size)
                y1 = (row * self.square_size)
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='black', fill=color, tags='field')
                color = self.switch_color(color)
        self.update_images()
        self.update_units(self.unit_objects)
        self.canvas.tag_raise('piece')
        self.canvas.tag_lower('field')

    def click_handler(self, event):
        col = event.x / self.square_size
        row = event.y / self.square_size

        try:
            unit = filter(lambda unit: unit.field.position == (row, col), self.unit_objects)[0]
        except:
            unit = None

        if not unit:
            self.message_queue.put(Message(type=MessageType.GAME_ACTION, action=GameAction(type=GameActionType.MOVE, target_pos=(row, col))))
        else: 
            if type(unit) == Player:
                self.message_queue.put(Message(type=MessageType.GAME_ACTION, action=GameAction(type=GameActionType.HEAL, target_pos=(row, col))))
            else:
                self.message_queue.put(Message(type=MessageType.GAME_ACTION, action=GameAction(type=GameActionType.ATTACK, target_pos=(row, col))))