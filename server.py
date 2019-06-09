import random


class Server:
    players = []

    def __init__(self, name):
        self.players.append({
            'name': name,
            'id': 1
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

        self.units = [
            {
                'x': 7,
                'y': 2,
                'n': 4
            }
        ]

        return {
            'map': self.map,
            'units': self.units
        }


if __name__ == '__main__':
    server = Server()
