from time import sleep
from datetime import datetime


class Limiter:
    def __init__(self, limit_count: int, seconds: int) -> None:
        self.limit_count = limit_count
        self.seconds = seconds
        self.count = 0
        self.time = datetime.timestamp(datetime.now())
        self.working_time = 0
        self.avg = 0

    def process(self) -> None:
        self.count += 1
        now = datetime.timestamp(datetime.now())
        dx = int(now - self.time)
        self.avg = (self.working_time+dx) / self.count
        if self.count % self.limit_count == 0 and dx < self.seconds:
            sleep(self.seconds - dx)
            self.working_time += dx
            self.time = datetime.timestamp(datetime.now())