import logging
from typing import List, Optional

from tcpoverudp.packet import Packet
from tcpoverudp.socket import Socket
from tcpoverudp.timer import Timer
from tcpoverudp.config import *
from threading import Lock


class Duplex:
    def __init__(self, socket: Socket):
        super().__init__()
        self.socket = socket
        self.receiver_expected_seq_num = 1
        self.receiver_send_packet = Packet(b'', ack=True, acknum=0)
        self.base = 1
        self.sender_next_seq_num = 1
        self.sender_send_packets: List[Optional[Packet]] = [None] * N
        self.send_lock = Lock()
        self.timer = Timer(self.timeout)

    def listen(self) -> bytes:
        while True:
            packet = self.socket.listen()
            if packet.ack:
                if not packet.is_corrupted():
                    self.base = packet.acknum + 1
                    logging.debug(f'got ack {packet.acknum}')
                    if self.base == self.sender_next_seq_num:
                        self.timer.stop_timer()
                    else:
                        self.timer.start_timer()
            else:
                if not packet.is_corrupted() and packet.seqnum == self.receiver_expected_seq_num:
                    self.receiver_send_packet = Packet(b'', ack=True, acknum=self.receiver_expected_seq_num)
                    self.socket.send(self.receiver_send_packet)
                    self.receiver_expected_seq_num += 1
                    return packet.data
                else:
                    self.socket.send(self.receiver_send_packet)

    def send(self, data: bytes) -> bool:
        if self.sender_next_seq_num < self.base + N:
            self.send_lock.acquire()
            self.sender_send_packets[self.sender_next_seq_num] = Packet(data, seqnum=self.sender_next_seq_num)
            self.socket.send(self.sender_send_packets[self.sender_next_seq_num])
            if self.base == self.sender_next_seq_num:
                self.timer.start_timer()
            self.sender_next_seq_num += 1
            self.send_lock.release()
        else:
            return False
        return True

    def timeout(self) -> None:
        self.timer.start_timer()
        self.send_lock.acquire()
        for i in range(self.base, self.sender_next_seq_num):
            logging.debug(f'base={self.base}; sender_nextseqnum={self.sender_next_seq_num}')
            self.socket.send(self.sender_send_packets[i])
        self.send_lock.release()
