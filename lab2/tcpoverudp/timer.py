import logging
from threading import Thread
from time import sleep

from tcpoverudp.config import TIMEOUT

STEP = 100


class Timer:
    def __init__(self, timeout: callable):
        self.task = None
        self.stop_flag = False
        self.thread = Thread(target=self._timer, name='Timer Thread', daemon=True)
        self.t_idx = 0
        self.timeout_handler = timeout

    def is_running(self):
        return not self.stop_flag

    def _timer(self):
        while True:
            if not self.stop_flag:
                self.t_idx += 1
                if self.t_idx == STEP:
                    self.stop_flag = True
                    self.t_idx = 0
                    logging.debug('timeout')
                    self.timeout_handler()
            sleep(TIMEOUT / STEP)

    def start_timer(self) -> None:
        logging.debug('timer started')
        if not self.thread.is_alive():
            self.thread.start()
        self.t_idx = 0
        self.stop_flag = False

    def stop_timer(self) -> None:
        logging.debug(f'timer stopped')
        self.stop_flag = True
        self.t_idx = 0
