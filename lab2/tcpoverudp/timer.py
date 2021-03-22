class Timer:
    def start_timer(self) -> None:
        raise RuntimeError

    def stop_timer(self) -> None:
        raise RuntimeError

    def timeout(self) -> None:
        raise NotImplementedError
