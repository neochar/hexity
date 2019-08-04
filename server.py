import json
import random
import socket


class Server:

    def __init__(self, name='unnamed'):

        self.sock = self.create_socket()

        self.players = []

        self.players.append({
            'name': 'AI-I',
            'id': 0,
        })
        self.players.append({
            'name': name,
            'id': 1,
        })
        self.players.append({
            'name': 'AI-II',
            'id': 2,
        })
        self.units = []
        self.map = []

        pass

    def create_socket(self):
        port = 9090
        sock = socket.socket()
        sock.bind(('', port))
        sock.listen(1)
        print('Socket is created on port {}'.format(port))
        return sock

    def get_map(self, map_w=None, map_h=None):
        """

        :param map_w:
        :param map_h:
        :return:
        """

        random.seed(7)
        self.map_w = map_w
        self.map_h = map_h
        # self.map = [
        #     [random.randint(0, 1) for _ in range(map_w)] for _ in range(map_h)
        # ]

        self.map = [
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        ]

        self.units.append({
            'x': 7,
            'y': 7,
            'n': 8,
            'player': self.players[0]
        })

        self.units.append({
            'x': 7,
            'y': 2,
            'n': 4,
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
            'units': self.units,
            'player_id': 1
        }

    def listen(self):
        print('Waiting for connection')
        conn, addr = self.sock.accept()
        print('Connection recieved from addr {}'.format(addr))
        while 1:
            try:
                request_raw = conn.recv(1024 * 10)
                request = json.loads(request_raw.decode('utf-8'))

                # validate request
                result = self.do_if_valid(request)
                response = {
                    'success': result['error'] is False,
                    'data': result['data'] or []
                }
                if result['error']:
                    response['message'] = result['error']

                self.sock.send(
                    str.encode(
                        json.dumps(response)
                    )
                )

                break
            except KeyboardInterrupt:
                self.shutdown()
        self.listen()

        pass

    def shutdown(self):
        self.sock.close()
        exit()

    def do_if_valid(self, request):
        """
        :param request:
        :return:
        """

        result = {
            'error': False
        }
        player_id = request['player']

        if request['command'] == 'move':
            # TODO Get new coordinates and check if move is possible
            pass
        elif request['command'] == 'attack':
            # TODO Calculate damage and result of attack
            pass
        elif request['command'] == 'end_of_turn':
            pass
        elif request['command'] == 'get_map':
            result['data'] = self.map

        return result


if __name__ == '__main__':
    server = Server()
    server.listen()
