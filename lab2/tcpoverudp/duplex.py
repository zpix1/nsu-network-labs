import logging

from tcpoverudp.packet import Packet
from tcpoverudp.socket import Socket
from tcpoverudp.timer import Timer
from tcpoverudp.config import *
from threading import Lock

class Duplex:
    def __init__(self, socket: Socket):
        super().__init__()
        self.socket = socket
        self.receiver_expectedseqnum = 1
        self.receiver_sendpkt = Packet(b'', acknum=0, ack=True)
        self.base = 1
        self.sender_nextseqnum = 1
        self.sender_sendpkt: List[Optional[Packet]] = [None] * N
        self.send_lock = Lock()
        self.timer = Timer(self.timeout)

    def listen(self) -> bytes:
        while True:
            packet = self.socket.listen()
            if packet.ack:
                if not packet.is_corrupted():
                    self.base = packet.acknum + 1
                    logging.debug(f'got ack {packet.acknum}, set base to {self.base} (sender_nextseqnum={self.sender_nextseqnum})')
                    if self.base == self.sender_nextseqnum:
                        self.timer.stop_timer()
                    else:
                        self.timer.start_timer()
            else:
                if not packet.is_corrupted() and packet.seqnum == self.receiver_expectedseqnum:
                    self.receiver_sendpkt = Packet(b'', ack=True, acknum=self.receiver_expectedseqnum)
                    self.socket.send(self.receiver_sendpkt)
                    self.receiver_expectedseqnum += 1
                    return packet.data
                else:
                    self.socket.send(self.receiver_sendpkt)

    def send(self, data: bytes) -> bool:
        if self.sender_nextseqnum < self.base + N:
            self.send_lock.acquire()
            self.sender_sendpkt[self.sender_nextseqnum] = Packet(data, seqnum=self.sender_nextseqnum)
            self.socket.send(self.sender_sendpkt[self.sender_nextseqnum])
            if self.base == self.sender_nextseqnum:
                self.timer.start_timer()
            self.sender_nextseqnum += 1
            self.send_lock.release()
        else:
            return False
        return True

    def timeout(self) -> None:
        self.timer.start_timer()
        self.send_lock.acquire()
        for i in range(self.base, self.sender_nextseqnum):
            logging.debug(f'base={self.base}; sender_nextseqnum={self.sender_nextseqnum}')
            self.socket.send(self.sender_sendpkt[i])
        self.send_lock.release()