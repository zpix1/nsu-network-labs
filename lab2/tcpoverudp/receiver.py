import logging

from tcpoverudp.packet import Packet
from tcpoverudp.socket import Socket


class Receiver:
    def __init__(self, socket: Socket):
        self.socket = socket
        self.expectedseqnum = 1
        self.sendpkt = Packet(0, b'', ack=True)

    def listen(self) -> None:
        while True:
            packet = self.socket.listen()
            if not packet.is_corrupted() and packet.seqnum == self.expectedseqnum:
                logging.info(f'Received: {packet}')
                self.sendpkt = Packet(self.expectedseqnum, b'', ack=True)
                self.socket.send(self.sendpkt)
                self.expectedseqnum += 1
            else:
                self.socket.send(self.sendpkt)
