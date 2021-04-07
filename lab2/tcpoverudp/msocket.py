import logging
from queue import Queue
from random import random
import pickle

import socket

from tcpoverudp.packet import Packet

LOSE_RATE = 0.4

PACK_SIZE = 400


def pack(packet: Packet):
    data = pickle.dumps(packet)
    if len(data) > PACK_SIZE:
        raise Exception('Packet is too big...')
    data = data.ljust(PACK_SIZE, b'\x00')
    return data


def unpack(data: bytes):
    # PWN, very bad, who cares?
    return pickle.loads(data)


class Socket:

    def __init__(self, addr='127.0.0.1', port1=8888, port2=9999, server=False):
        self.server = server
        self.addr = addr
        self.port1 = port1
        self.port2 = port2
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.udp_socket.bind((addr, port1))
        logging.debug(f'server socket binded to {port1}')

        self.conn = None

        self.queue = Queue()
        self.out_socket = None

    def set_out_socket(self, socket: 'Socket'):
        self.out_socket = socket

    def send(self, packet: Packet) -> None:
        if random() < LOSE_RATE:
            logging.error(f'lost {packet}')
            return
        logging.debug(f'sent {packet}')
        # self.out_socket.queue.put(packet)
        self.udp_socket.sendto(pack(packet), (self.addr, self.port2))

    def listen(self) -> Packet:
        # packet = self.queue.get()
        logging.debug(f'{self}, listening')
        data = self.udp_socket.recv(PACK_SIZE)
        packet = unpack(data)
        logging.debug(f'{self}, received {packet}')
        return packet