from time import sleep

from tcpoverudp.receiver import Receiver
from tcpoverudp.sender import Sender
from tcpoverudp.socket import Socket

def main():
    socket = Socket()

    receiver = Receiver(socket)
    sender = Sender(socket)

    receiver.listen()
    sender.listen()

    data = [
        b'kek',
        b'mem'
    ]

    for d in data:
        sender.send(d)
        sleep(1)

main()