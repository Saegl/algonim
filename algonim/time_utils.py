import time


class Timer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        print(f"<{self.name}>: Started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.perf_counter()
        elapsed = end - self.start
        print(f"<{self.name}>: Took {elapsed:.3f} seconds")
