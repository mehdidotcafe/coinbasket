from random import uniform


class RandomGenerator:
    def generate_number(self, min: int, max: int):
        return int(uniform(min, max))
