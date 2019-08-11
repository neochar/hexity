import os
import random
from getch import getch
import socket
import json


class format:
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
    players = [
        {
            'color': format.RED
        },
        {
            'color': format.BLUE
        },
        {
            'color': format.GREEN
        }
    ]

    def __init__(self, name=None):
        self.player = 1
        self.awaiting_quit_confirmation = None
        self.moves_left = None
        self.is_end_of_turn = False
        self.power_left = None
        self.cursor_char = '*'
        self.name = name
        self.cursor = []
        self.unit_selected = None
        self.sock = None

    def connect(self):
        """
        Connect to server
        """

        # self.server = Server(self.name)

        self.sock = self.create_socket()
        self.get_game()

        pass

    def run(self):
        """
        Infinie game cycle
        """

        while 1:
            try:
                self.update()
                self.render()
                self.input()
            except KeyboardInterrupt:
                self.shutdown()

        pass

    def render(self, do_hex=True):
        """
        Render the map and units
        :param do_hex:
        """

        # os.system('cls') # Windows only
        # os.system('clear')

        output = []

        line = []
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                unit = self.find_unit(x, y)
                if [x, y] == self.cursor:
                    if unit and self.unit_selected == unit:
                        line.append(' {}{}{}'.format(
                            format.BOLD,
                            unit['n'],
                            format.END
                        ))
                    elif unit:
                        line.append(' {}'.format(
                            unit['n'],
                        ))
                    else:
                        line.append(' {}'.format(self.cursor_char))
                elif unit is not None:
                    unit_char = '{}{}{}'.format(
                        self.players[unit['player']['id']]['color'],
                        unit['n'],
                        format.END
                    )
                    if self.unit_selected == unit:
                        line.append(' {}{}{}'.format(
                            format.BOLD,
                            unit_char,
                            format.END
                        ))
                    else:
                        line.append(' {}'.format(unit_char))
                else:
                    # Cell == 1 -> ground, cell == 0 -> space
                    if cell == 0:
                        line.append(' .')
                    else:
                        line.append('  ')
            output.append(line)
            line = []
            if y % 2 == 0 and do_hex:
                line.append(' ')

        # Render map
        print('\n'.join(''.join(line) for line in output))
        print()

        # Render info
        print(self.cursor)

        if self.is_end_of_turn:
            if self.power_left > 0:
                print('Power left: {}'.format(self.power_left))
            else:
                print('Press enter key to end move')
        else:
            if self.moves_left > 0:
                print('Moves left: {}'.format(self.moves_left))
            else:
                print('Press enter key to end move')
        if self.unit_selected:
            print('Unit selected: x={}, y={}, n={}'.format(
                self.unit_selected['x'],
                self.unit_selected['y'],
                self.unit_selected['n'],
            ))
        else:
            if self.is_end_of_turn:
                if self.power_left:
                    print('Use space to increase power of unit')
                else:
                    print()
            else:
                if self.moves_left:
                    print('Use space key to select unit')
                else:
                    print()

        if self.awaiting_quit_confirmation:
            print('To quit press q again')
        else:
            print()

        print('\n' * 6)

    def input(self):
        """

        :return:
        """

        try:
            command = getch()
        except OverflowError:
            return

        if command == 'h':
            self.move_cursor(-1, 0)
        elif command == 'j':
            self.move_cursor(0, 1)
        elif command == 'k':
            self.move_cursor(0, -1)
        elif command == 'l':
            self.move_cursor(1, 0)
        elif command == ' ':
            self.action()
        elif command == '\n':
            self.end_of_turn()
        elif command == 'q':
            self.quit()
        elif command == chr(27):
            self.cancel()

        pass

    def move_cursor(self, dx, dy):
        """
        :param dx:
        :param dy:
        :return:
        """
        cursor_new = self.cursor.copy()
        cursor_new[0] += dx
        cursor_new[1] += dy

        is_y_odd = cursor_new[1] % 2 != 0

        limits = [
            cursor_new[0] < 0,
            cursor_new[0] == self.map_w,
            cursor_new[1] < 0,
            cursor_new[1] == self.map_h
        ]
        if any(limits):
            return

        if self.unit_selected:
            if abs(self.unit_selected['y'] - cursor_new[1]) > 1:
                return
            if abs(self.unit_selected['x'] - cursor_new[0]) > 1:
                return
            if is_y_odd:
                if self.unit_selected['y'] % 2 == 0:
                    if self.cursor[0] > self.unit_selected['x'] and dy:
                        cursor_new[0] -= 1
                    if cursor_new[0] > self.unit_selected['x']:
                        return
                else:
                    if self.cursor[0] < self.unit_selected['x'] and dy:
                        cursor_new[0] += 1
            else:
                if self.unit_selected['y'] % 2 != 0:
                    if self.cursor[0] < self.unit_selected['x'] and dy:
                        cursor_new[0] += 1
                    if cursor_new[0] < self.unit_selected['x']:
                        return

        if self.map[cursor_new[1]][cursor_new[0]] != 0:
            if dy:
                if not is_y_odd:
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

    def action(self):
        """

        :return:
        """

        # `unit` is what we have under cursor
        unit_under_cursor = self.find_unit(self.cursor[0], self.cursor[1])

        if not self.is_end_of_turn:
            if self.unit_selected:
                if [
                    self.unit_selected['x'],
                    self.unit_selected['y']
                ] == self.cursor:
                    self.unselect_unit()
                    return
                else:
                    if not uni_under_cursort:
                        # Unit movement
                        unit_new = self.unit_selected.copy()
                        unit_new['n'] -= 1
                        unit_new['x'] = self.cursor[0]
                        unit_new['y'] = self.cursor[1]
                        unit_old = self.find_unit(
                            self.unit_selected['x'],
                            self.unit_selected['y']
                        )
                        self.unit_reset(unit_old)
                        if unit_new['n'] == 1:
                            self.unselect_unit()
                        else:
                            self.unit_selected = unit_new.copy()
                        self.units.append(unit_new)
                        return
                    elif unit_under_cursor['player']['id'] != self.player:
                        # Unit attack
                        self.attack(unit_under_cursor)

        # Make sure we select / powerup our player un_under_cursorit
        if unit_under_cursor and unit_under_cursor['player'][
            'id'] == self.player:
            if self.is_end_of_turn:
                # Unit powerup
                if unit_under_cursor and self.power_left > 0:
                    if self.unit_power_up(unit_under_cursor):
                        self.power_left -= 1
            else:
                # unit_under_cursor['n'] is unit power (1, 2, 3, ... 8)
                if any([
                    unit_under_cursor is None,
                    unit_under_cursor['n'] < 2
                ]):
                    return
                # Unit selection
                self.unit_selected = unit_under_cursor.copy()
        pass

    def unit_reset(self, unit):
        unit['n'] = 1

    def unit_power_up(self, unit):
        if unit['n'] < 8:
            unit['n'] += 1
            return True
        return False

    def count_power(self):
        """
        TODO Make sure end of turn check is neccessary
        """
        if not self.is_end_of_turn:
            self.power_left = len([unit for unit in self.units if
                                   unit['player']['id'] == self.player])
        pass

    def end_of_turn(self):
        if self.is_end_of_turn:
            self.new_turn()
            return

        self.unselect_unit()
        self.count_power()
        self.is_end_of_turn = True
        pass

    def unselect_unit(self):
        self.unit_selected = None

    def new_turn(self):
        self.is_end_of_turn = False
        pass

    def update(self):
        """
        Do update game counters
        """

        # self.count_power()
        self.count_moves()
        pass

    def count_moves(self):
        self.moves_left = 0
        for unit in self.units:
            self.moves_left += unit['n'] \
                if unit['n'] > 1 and unit['player']['id'] == self.player \
                else 0
        pass

    def quit(self):
        if self.awaiting_quit_confirmation:
            os.system('clear')
            exit()
        self.awaiting_quit_confirmation = True
        pass

    def cancel(self):
        self.unselect_unit()
        pass

    def attack(self, unit):
        # TODO Move this part to server
        # TODO Get damage and update units
        probability = .0
        diff = self.unit_selected['n'] - unit['n']
        if diff >= 2:
            probability = 1.0
        elif diff == 1:
            probability = .75
        elif diff == 0:
            probability = .5
        elif diff == -1:
            probability = .25

        if probability >= random.random():
            # Unit killed
            unit['player']['id'] = self.player
            unit['n'] = self.unit_selected['n'] - unit['n']
            if unit['n'] < 1:
                unit['n'] = 1

        self.unit_reset(
            self.find_unit(
                self.unit_selected['x'],
                self.unit_selected['y']
            )
        )
        if unit['n'] > 1:
            self.unit_selected = unit.copy()

        pass

    def shutdown(self):
        self.sock.close()
        exit()

    def create_socket(self):
        """

        :return:
        """
        sock = socket.socket()
        sock.connect(('localhost', 9090))

        return sock

        pass

    def send(self, command, data=None):
        """
        :param command:
        :param data:
        """
        request = {
            'player': self.player,
            'command': command,
            'data': data
        }

        self.sock.send(str.encode(
            json.dumps(request)
        ))

        response_raw = self.sock.recv(1024 * 10)
        print(response_raw)
        exit()
        response = json.loads(
            response_raw.decode('utf-8')
        )

        if response['success'] is False:
            print(response['message'])
            self.shutdown()

        return response['data']

    def get_game(self):
        map = self.send('get_map')

        self.map_w = len(map['map'][0])
        self.map_h = len(map['map'])
        self.map = map['map']
        self.units = map['units']

        self.cursor = [
            random.randint(0, self.map_w),
            random.randint(0, self.map_h) - 2,
        ]
        pass


def main():
    # name = input('Your name: ')
    name = 'neochar'
    client = Client(name)
    client.connect()
    # client.run()


if __name__ == '__main__':
    main()
