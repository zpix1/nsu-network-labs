from collections import Callable

from tcpoverudp.packet import Packet


class Socket:
    def __init__(self):
        raise NotImplementedError

    def send(self, packet: Packet) -> None:
        raise NotImplementedError

    def listen(self) -> Packet:
        raise NotImplementedError
