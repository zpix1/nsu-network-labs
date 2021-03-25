import asyncio
import logging
import sys
from threading import Thread
from time import sleep

from tcpoverudp.receiver import Receiver
from tcpoverudp.sender import Sender
from tcpoverudp.socket import Socket
from tcpoverudp.timer import Timer


def spamer(sender: Sender):
    for d in [
        b'kek',
        b'mem'
    ]:
        logging.info(f'sent data "{d.decode()}"')
        sender.send(d)
        sleep(1)


def main():
    logging.basicConfig(level=logging.DEBUG)

    socket_r = Socket()
    socket_l = Socket()

    socket_r.set_out_socket(socket_l)
    socket_l.set_out_socket(socket_r)

    receiver = Receiver(socket_r)
    sender = Sender(socket_l)
    sender.listen()

    Thread(target=spamer, args=[sender]).start()

    while True:
        logging.info(f'got data "{receiver.listen().decode()}"')


if __name__ == "__main__":
    main()
