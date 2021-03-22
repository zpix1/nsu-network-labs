from threading import Thread
from typing import Optional, List

from tcpoverudp.config import N
from tcpoverudp.packet import Packet
from tcpoverudp.timer import Timer
from tcpoverudp.socket import Socket


class Sender(Timer):
    def __init__(self, socket: Socket):
        super().__init__()
        self.base = 1
        self.nextseqnum = 1
        self.sendpkt: List[Optional[Packet]] = [None] * N
        self.socket = socket

    def send(self, data: bytes) -> bool:
        if self.nextseqnum < self.base + N:
            self.sendpkt[self.nextseqnum] = Packet(self.nextseqnum, data)
            self.socket.send(self.sendpkt[self.nextseqnum])
            if self.base == self.nextseqnum:
                self.start_timer()
                self.nextseqnum += 1
        else:
            return False
        return True

    def timeout(self) -> None:
        self.start_timer()
        for i in range(self.base, self.nextseqnum):
            self.socket.send(self.sendpkt[i])

    def listen(self) -> None:
        thread = Thread(target=self._listen)
        thread.start()

    def _listen(self) -> None:
        while True:
            packet = self.socket.listen()
            if not packet.is_corrupted():
                self.base = packet.seqnum
                if self.base == self.nextseqnum:
                    self.stop_timer()
                else:
                    self.start_timer()
