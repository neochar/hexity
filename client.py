import os
import random
import time
from getch import getch
from server import Server
from pprint import pprint


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Client:

    def __init__(self, name=None):
        self.cursor_char = '*'
        self.name = name
        self.cursor = []
        self.selection = []
        self.sel_unit = None

    def connect(self):
        self.server = Server(self.name)
        self.map_w = 10
        self.map_h = 10
        map = self.server.get_map(
            self.map_w,
            self.map_h
        )
        self.map = map['map']
        self.units = map['units']
        self.cursor = [
            random.randint(0, self.map_w),
            random.randint(0, self.map_h) - 2,
        ]
        pass

    def run(self):
        while (1):
            self.render()
            self.input()
        pass

    def render(self):
        # os.system('cls') # Windows only
        # os.system('clear')

        output = []

        line = []
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                unit = self.find_unit(x, y)
                if [x, y] == self.cursor:
                    if unit:
                        line.append(' {}{}{}'.format(
                            color.BOLD,
                            unit['n'],
                            color.END
                        ))
                    else:
                        line.append(' {}'.format(self.cursor_char))
                elif unit is not None:
                    unit_char = '{}{}{}'.format(
                        color.BLUE,
                        unit['n'],
                        color.END
                    )
                    if self.sel_unit == unit:
                        line.append(' {}{}{}'.format(
                            color.BOLD,
                            unit_char,
                            color.END
                        ))
                    else:
                        line.append(' {}'.format(unit_char))
                else:
                    if cell == 0:
                        line.append(' .')
                    else:
                        line.append('  ')
            output.append(line)
            line = []
            # if y % 2 == 0:
            #     line.append('>')

        print('\n'.join(''.join(line) for line in output))
        print(self.cursor)
        print('\n' * 9)

    def input(self):
        try:
            command = getch()
        except OverflowError:
            return

        if command == 'h':
            self.move_cursor_x(-1)
        elif command == 'j':
            self.move_cursor_y(1)
        elif command == 'k':
            self.move_cursor_y(-1)
        elif command == 'l':
            self.move_cursor_x(1)
        elif command == ' ':
            self.select()

        pass

    def move_cursor_x(self, dx):
        cursor_new = self.cursor.copy()
        cursor_new[0] += dx
        if cursor_new[0] < 0 or cursor_new[0] == self.map_w:
            return
        if self.sel_unit:
            if abs(self.sel_unit['x'] - cursor_new[0]) > 1:
                return
        if self.map[cursor_new[1]][cursor_new[0]] != 0:
            return

        self.cursor = cursor_new
        pass

    def move_cursor_y(self, dy):
        cursor_new = self.cursor.copy()
        cursor_new[1] += dy
        if cursor_new[1] < 0 or cursor_new[1] == self.map_h:
            return
        if self.sel_unit:
            if abs(self.sel_unit['y'] - cursor_new[1]) > 1:
                return
        if self.map[cursor_new[1]][cursor_new[0]] != 0:
            if cursor_new[1] % 2 == 0:
                rg = [1]
            else:
                rg = [-1]
            for i in rg:
                try:
                    if self.map[cursor_new[1]][cursor_new[0] + i] == 0:
                        cursor_new[0] += i
                        self.cursor = cursor_new
                        return
                except IndexError:
                    return
            return

        self.cursor = cursor_new
        pass

    def find_unit(self, x, y):
        for unit in self.units:
            if unit['x'] == x and unit['y'] == y:
                return unit
        return None

    def select(self):
        if self.selection == self.cursor:
            self.selection = None
            self.sel_unit = None
            return
        unit = self.find_unit(self.cursor[0], self.cursor[1])
        if unit is None:
            return
        self.sel_unit = unit.copy()
        self.selection = self.cursor.copy()
        pass


def main():
    # name = input('Your name: ')
    name = 'neochar'
    client = Client(name)
    client.connect()
    client.run()


if __name__ == '__main__':
    main()
