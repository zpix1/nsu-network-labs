import logging
from queue import Queue
from random import random

from tcpoverudp.packet import Packet


class Socket:
    def __init__(self):
        self.queue = Queue()
        self.out_socket = None

    def set_out_socket(self, socket: 'Socket'):
        self.out_socket = socket

    def send(self, packet: Packet) -> None:
        if random() < 0.1:
            logging.info(f'lost {packet}')
            return
        logging.info(f'sent {packet}')
        self.out_socket.queue.put(packet)

    def listen(self) -> Packet:
        packet = self.queue.get()
        logging.info(f'received {packet}')
        return packet
