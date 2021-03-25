import logging
from threading import Lock, Thread
from typing import Optional, List

from tcpoverudp.config import N
from tcpoverudp.packet import Packet
from tcpoverudp.timer import Timer
from tcpoverudp.socket import Socket


class Sender:
    def __init__(self, socket: Socket):
        super().__init__()
        self.base = 1
        self.nextseqnum = 1
        self.sendpkt: List[Optional[Packet]] = [None] * N
        self.socket = socket
        self.send_lock = Lock()
        self.timer = Timer(self.timeout)

    def send(self, data: bytes) -> bool:
        if self.nextseqnum < self.base + N:
            self.send_lock.acquire()
            self.sendpkt[self.nextseqnum] = Packet(data, seqnum=self.nextseqnum)
            self.socket.send(self.sendpkt[self.nextseqnum])
            if self.base == self.nextseqnum:
                self.timer.start_timer()
            self.nextseqnum += 1
            self.send_lock.release()
        else:
            return False
        return True

    def timeout(self) -> None:
        self.timer.start_timer()
        self.send_lock.acquire()
        for i in range(self.base, self.nextseqnum):
            logging.debug(f'base={self.base}; nextseqnum={self.nextseqnum}')
            self.socket.send(self.sendpkt[i])
        self.send_lock.release()

    def listen(self) -> None:
        thread = Thread(target=self._listen)
        thread.start()

    def _listen(self) -> None:
        while True:
            packet = self.socket.listen()
            if not packet.is_corrupted() and packet.ack:
                self.base = packet.acknum + 1
                logging.debug(f'got ack {packet.seqnum}, set base to {self.base} (nextseqnum={self.nextseqnum})')
                if self.base == self.nextseqnum:
                    self.timer.stop_timer()
                else:
                    self.timer.start_timer()
