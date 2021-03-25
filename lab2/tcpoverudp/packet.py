import logging
from dataclasses import dataclass


@dataclass
class Packet:
    seqnum: int
    data: bytes
    ack: bool
    acknum: int

    def __init__(self, data: bytes = b'', seqnum: int = None, ack: bool = False, acknum: int = None):
        self.seqnum = seqnum
        self.data = data
        self.ack = ack
        self.acknum = acknum

    def is_corrupted(self):
        return False
