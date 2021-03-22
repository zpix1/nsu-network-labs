import logging
from dataclasses import dataclass


@dataclass
class Packet:
    seqnum: int
    data: bytes
    ack: bool

    def __init__(self, seqnum: int, data: bytes, ack: bool = False):
        self.seqnum = seqnum
        self.data = data
        self.ack = ack

    def is_corrupted(self):
        return False
