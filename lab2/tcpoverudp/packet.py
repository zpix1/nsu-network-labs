import logging
from dataclasses import dataclass


@dataclass
class Packet:
    seqnum: int
    data: bytes
    ack: bool
    acknum: int
    is_acked: bool
    syn: bool

    def __init__(self, data: bytes = b'', seqnum: int = None, ack: bool = False, acknum: int = None, syn: bool = False):
        self.seqnum = seqnum
        self.data = data
        self.ack = ack
        self.acknum = acknum
        self.is_acked = False
        self.syn = syn

    def is_corrupted(self):
        return False
