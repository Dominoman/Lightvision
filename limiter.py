import time
from datetime import datetime


class Limiter:
    def __init__(self, process_count: int, ms: int) -> None:
        self.ms = ms
        self.process_count = process_count
        self.now = datetime.now()
        self.count = 0

    def process(self) -> None:
        self.count += 1
        if self.count % self.process_count == 0:
            difference = (datetime.now() - self.now).total_seconds()
            if difference < self.ms:
                time.sleep(self.ms-difference)
                self.now = datetime.now()
