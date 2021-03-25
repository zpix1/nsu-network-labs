import logging
from threading import Thread
from time import sleep

from tcpoverudp.config import TIMEOUT

STEP = 1000

class Timer:
    def __init__(self, timeout: callable):
        self._task = None
        self._stop = False
        self._thread = Thread(target=self._timer, name='Timer Thread')
        self._t = 0
        self._timeout = timeout

    def _timer(self):
        while True:
            if not self._stop:
                self._t += 1
                if self._t == STEP:
                    self._stop = True
                    self._t = 0
                    logging.debug('timeout')
                    self._timeout()
            sleep(TIMEOUT / STEP)

    def start_timer(self) -> None:
        logging.debug('timer started')
        if not self._thread.is_alive():
            self._thread.start()
        self._t = 0
        self._stop = False

    def stop_timer(self) -> None:
        logging.debug(f'timer stopped {self._t} {self._thread}')
        self._stop = True
        self._t = 0
