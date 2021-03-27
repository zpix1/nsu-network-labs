import logging
from threading import Thread
from time import sleep

from tcpoverudp.duplex import Duplex
from tcpoverudp.packet import Packet
from tcpoverudp.socket import Socket
from tcpoverudp.tcp import TCP


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
        logging.info(f'TCP {name} got data {duplex.listen().data}')


def main():
    logging.basicConfig(level=logging.DEBUG)

    socket_r = Socket()
    socket_l = Socket()

    socket_r.set_out_socket(socket_l)
    socket_l.set_out_socket(socket_r)

    receiver = TCP(socket_r)
    sender = TCP(socket_l)

    Thread(target=listen, args=[sender, "sender"]).start()
    Thread(target=listen, args=[receiver, "receiver"]).start()
    sleep(1)

    Thread(target=spam, args=[sender]).start()


if __name__ == "__main__":
    main()
