import asyncio
from soxprotocol import SoxClientProtocol, SoxServerProtocol

try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair

class ThinSox():
    _host = "127.0.0.1"
    _port = "8000"
    _loop = asyncio.get_event_loop()
    _username = ""
    _transport = None
    _protocol = None

    def __init__(self):
        self._rsock, self._wsock = socketpair()

    def run(self):
        try:
            self.read_messages()
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            if self._rsock:
                self._rsock.close()
            if self._transport:
                self._transport.close()
            self._loop.close()
            return

    def read_messages(self):
        connect = self._loop.create_datagram_endpoint(
            SoxServerProtocol,
            local_addr=(self._host, self._port)
        )
        self._loop.run_until_complete(connect)

    def send_message(self, message):
        # Prepend the username, per sox protocol
        message = self._username + message
        prefix = self._host.split('.')[:-1]
        prefix = '.'.join(prefix) + '.'

        for i in range(1,255):
            connect = self._loop.create_datagram_endpoint(
                lambda: SoxClientProtocol(message, self._loop),
                remote_addr=(prefix + str(i), self._port)
            )
            self._loop.run_until_complete(connect)

    def set_username(self, username):
        temp = username
        if len(username) < 5:
            pad = 5 - len(username)
            for i in range(pad):
                temp = temp + " "

        self._username = temp

    def set_host(self, host):
        self._host = host

    def set_port(self, port):
        self._port = port
