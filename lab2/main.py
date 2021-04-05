import logging
from threading import Thread
from time import sleep

from tcpoverudp.duplex import Duplex
from tcpoverudp.packet import Packet
from tcpoverudp.msocket import Socket


def spam(sender: Duplex):
    for d in [
        b'kek',
        b'mem'
    ]:
        logging.info(f'sent data {d}')
        sender.send(Packet(d))
        sleep(1)


def listen(duplex: Duplex, name: str):
    while True:
        logging.info(f'Duplex {name} got data {duplex.listen().data}')


def main():
    logging.basicConfig(level=logging.INFO)

    socket_r = Socket()
    socket_l = Socket()

    socket_r.set_out_socket(socket_l)
    socket_l.set_out_socket(socket_r)

    receiver = Duplex(socket_r)
    sender = Duplex(socket_l)

    Thread(target=spam, args=[sender]).start()
    Thread(target=spam, args=[receiver]).start()
    Thread(target=listen, args=[sender, "sender"]).start()
    Thread(target=listen, args=[receiver, "receiver"]).start()


if __name__ == "__main__":
    main()
