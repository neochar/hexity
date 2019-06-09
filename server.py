import random


class Server:
    players = []

    def __init__(self, name):
        self.players.append({
            'name': 'AI',
            'id': 0
        })
        self.players.append({
            'name': name,
            'id': 1
        })
        self.players.append({
            'name': name,
            'id': 2
        })

        pass

    def get_map(self, map_w=None, map_h=None):
        random.seed(7)
        self.map_w = map_w
        self.map_h = map_h
        # self.map = [
        #     [random.randint(0, 1) for _ in range(map_w)] for _ in range(map_h)
        # ]

        self.map = [
            [0,0,0,1,1,0,0,0,0,0],
            [0,0,1,1,0,0,0,0,0,0],
            [0,0,1,1,1,0,0,0,0,0],
            [0,0,1,1,1,0,0,0,0,0],
            [0,0,0,1,1,0,0,0,0,0],
            [0,0,0,1,1,0,0,0,0,0],
            [0,0,1,1,1,1,1,0,0,0],
            [0,0,0,1,1,1,1,0,0,0],
            [1,1,0,0,0,0,0,0,0,0],
            [1,1,1,1,0,0,0,0,0,0],

        ]
        self.units = []

        self.units.append({
            'x': 7,
            'y': 7,
            'n': 2,
            'player': self.players[0]
        })

        self.units.append({
            'x': 7,
            'y': 2,
            'n': 9,
            'player': self.players[1]
        })

        self.units.append({
            'x': 0,
            'y': 1,
            'n': 6,
            'player': self.players[2]
        })

        return {
            'map': self.map,
            'units': self.units
        }


if __name__ == '__main__':
    server = Server()
