import time


class RateLimiter:

    def __init__(self, rate_per_sec: int):
        self.delay = 1 / rate_per_sec
        self.last_call = 0

    def wait(self):

        elapsed = time.time() - self.last_call

        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        self.last_call = time.time()