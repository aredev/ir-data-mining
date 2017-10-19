from random import random


class Dummy:
    def __init__(self):
        super().__init__()
        self.value = random()

    def get_random(self):
        return self.value
