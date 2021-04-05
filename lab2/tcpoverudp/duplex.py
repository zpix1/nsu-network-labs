import logging
from typing import List, Optional

from tcpoverudp.packet import Packet
from tcpoverudp.msocket import Socket
from tcpoverudp.timer import Timer
from tcpoverudp.config import *
from threading import Lock


class Duplex:
    def __init__(self, socket: Socket):
        self.socket = socket
        self.receiver_expected_seq_num = 1
        self.receiver_send_packet = Packet(b'', ack=True, acknum=0)
        self.base = 1
        self.sender_next_seq_num = 1
        self.sender_send_packets: List[Optional[Packet]] = [None] * N
        self.send_lock = Lock()
        self.timer = Timer(self.timeout)

    def listen(self) -> Packet:
        while True:
            packet = self.socket.listen()

            if packet.ack:
                for p in self.sender_send_packets:
                    if p:
                        if p.seqnum > packet.acknum:
                            break
                        p.is_acked = True
                        logging.debug(f'Got ack ({packet}) for {p}')
                if packet.acknum > self.base:
                    self.base = packet.acknum
                    if any(map(lambda p: p and p.is_acked, self.sender_send_packets)):
                        self.timer.start_timer()
            else:
                logging.debug(f'received packet {packet}, {self.receiver_expected_seq_num}')
                if packet.seqnum == self.receiver_expected_seq_num:
                    self.receiver_send_packet = Packet(b'', ack=True, acknum=self.receiver_expected_seq_num)
                    self.socket.send(self.receiver_send_packet)
                    self.receiver_expected_seq_num += 1
                    return packet
                else:
                    self.socket.send(self.receiver_send_packet)

    def send(self, orig_packet: Packet) -> bool:
        if self.sender_next_seq_num < self.base + N:
            self.send_lock.acquire()
            orig_packet.seqnum = self.sender_next_seq_num
            self.sender_send_packets[self.sender_next_seq_num] = orig_packet
            self.socket.send(self.sender_send_packets[self.sender_next_seq_num])
            if not self.timer.is_running():
                self.timer.start_timer()
            self.sender_next_seq_num += 1

            self.send_lock.release()
        else:
            return False
        return True

    def timeout(self) -> None:
        self.send_lock.acquire()

        for packet in self.sender_send_packets:
            if packet and not packet.is_acked:
                logging.debug(f'Resending {packet}')
                self.socket.send(packet)
                self.timer.start_timer()
                break

        self.send_lock.release()
