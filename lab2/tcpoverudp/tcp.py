import logging
from threading import Lock

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
        self.state = TCPState.CLOSED
        self.duplex = Duplex(socket)
        self.connection_established = Lock()
        self.connection_established.acquire()

    def listen(self) -> bytes:
        while True:
            packet = self.duplex.listen()
            if packet.syn:
                if self.state == TCPState.CLOSED:
                    self.duplex.send(Packet(b'', syn=True))
                    self.state = TCPState.SYN_SENT
                    logging.info('set to SYN_SENT')
                elif self.state == TCPState.SYN_SENT:
                    self.state = TCPState.ESTABLISHED
                    self.duplex.send(Packet(b'', syn=True))
                    logging.info('set to ESTABLISHED')
                    self.connection_established.release()
            else:
                return packet.data

    def send(self, data: bytes) -> bool:
        if self.state == TCPState.ESTABLISHED:
            return self.duplex.send(Packet(data))
        return False

    def establish(self):
        self.duplex.send(Packet(b'', syn=True))
        self.state = TCPState.SYN_SENT
        self.connection_established.acquire()
        self.connection_established.release()

