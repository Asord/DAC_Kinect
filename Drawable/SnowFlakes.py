from Drawable import drawable
from Utilities.Vector import Vector2

from random import randint
from pygame import draw

class Snowflakes(drawable):

    def __init__(self, bound):

        self.pos = Vector2.randValue((0, bound[0]), (1, 2))
        self.size = randint(10, 25)

        self._transform = Vector2.randValue((-2, 2), (1, 5))
        self._bound = bound

        self.color = (255, 255, 255)

    def update(self, bound, bodyParts):

        self.pos += self._transform

        self._bound = bound

    def draw(self, surface):

        draw.circle(surface, self.color, self.pos.toTuple(), self.size, 0)

    def isOutside(self):

        if self.pos.x < 0 or self.pos.x > self._bound[0]:
            return True
        if self.pos.y < 0 or self.pos.y > self._bound[1]:
            return True
        return False