import logging
from threading import Thread
from time import sleep

from tcpoverudp.config import TIMEOUT

STEP = 100


class Timer:
    def __init__(self):
        self._task = None
        self._stop = False
        self._thread = Thread(target=self._timer, name='Timer Thread')
        self._t = 0
        self._thread.start()

    def _timer(self):
        while True:
            if not self._stop:
                self._t += 1
                if self._t == STEP:
                    self._stop = True
                    self._t = 0
                    logging.info('timeout')
                    self.timeout()
            sleep(TIMEOUT / STEP)

    def start_timer(self) -> None:
        logging.info('timer started')
        self._t = 0
        self._stop = False

    def stop_timer(self) -> None:
        logging.info('timer stopped')
        self._stop = True
        self._t = 0

    def timeout(self) -> None:
        raise NotImplementedError
