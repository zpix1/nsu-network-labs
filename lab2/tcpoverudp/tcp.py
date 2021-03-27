import logging

from tcpoverudp.duplex import Duplex
from tcpoverudp.packet import Packet
from tcpoverudp.socket import Socket
from enum import Enum


class TCPState(Enum):
    CLOSED = 1
    SYN_SENT = 2
    ESTABLISHED = 3


class TCP:
    def __init__(self, socket: Socket):
        self.socket = socket
        self.state = TCPState.CLOSED
        self.duplex = Duplex(socket)

        self.socket.send(Packet(b'', syn=True))
        self.state = TCPState.SYN_SENT

    def listen(self) -> bytes:
        while True:
            packet = self.duplex.listen()
            logging.critical(f'{packet}')
            if packet.syn:
                if self.state == TCPState.CLOSED:
                    self.duplex.send(Packet(b'', syn=True))
                    self.state = TCPState.SYN_SENT
                    logging.info('set to SYN_SENT')
                elif self.state == TCPState.SYN_SENT:
                    self.state = TCPState.ESTABLISHED
                    logging.info('set to ESTABLISHED')
            else:
                return packet.data

    def send(self, data: bytes) -> bool:
        if self.state == TCPState.ESTABLISHED:
            return self.duplex.send(Packet(data))
        return False
