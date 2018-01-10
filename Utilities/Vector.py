from math import sqrt, radians, pi
from math import sin as math_sin, cos as math_cos

from Utilities.globals import Globals

from pygame import draw

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def fromKinectPoint(cls, ColorSpacePoint):
        return cls(ColorSpacePoint.x, ColorSpacePoint.y)

    @classmethod
    def fromTuple(cls, tu):
        return cls(tu[0], tu[1])

    @classmethod
    def zero(cls):
        return cls(0, 0)

    @staticmethod
    def isVector(obj):
        return type(obj) is Vector2

    @staticmethod
    def toRect(vect1, vect2):
        return vect1.toTuple(), vect2.toTuple()

    @classmethod
    def randValue(cls, x=(0, 10), y=(0, 1)):
        from random import randrange
        return cls(randrange(x[0], x[1]), randrange(y[0], y[1]))

    @classmethod
    def fromPoints(cls, pointA, pointB):
        return cls(pointB.x - pointA.x, pointB.y - pointA.y)

    def toTuple(self):
        return int(self.x), int(self.y)

    def resize(self, new_size):
        len = self.len()
        if len < 1:
            _ratio = new_size
        else:
            _ratio = new_size / len
        return self.ratio(_ratio)

    def ratio(self, value):
        return Vector2(self.x * value, self.y * value)

    def deg_rotate(self, angle):
        return self.rad_rotate(radians(angle % 360))

    def rad_rotate(self, angle):
        sin = math_sin(pi * angle)
        cos = math_cos(pi * angle)

        new_x = (cos * self.x) - (sin * self.y)
        new_y = (sin * self.x) + (cos * self.y)
        return Vector2(new_x, new_y)

    def projectOn(self, other):
        return self.dot(other.normalize())

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)

    def normalize(self):
        x = self.x/self.len()
        y = self.y/self.len()
        return Vector2(x, y)

    def draw(self, surface, start_pt, color=(0, 255, 0), line_size=5):
        if not 'Debug' in Globals: return

        end_pt = start_pt + self
        draw.line(surface, color, start_pt.toTuple(), end_pt.toTuple(), line_size)

    def len(self):
        return sqrt(self.x **2 + self.y ** 2)

    def __len__(self):
        return self.len()

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __gt__(self, other):
        return self.y > other.y

    def __lt__(self, other):
        return self.y < other.y

    def __le__(self, other):
        return self.y <= other.y

    def __ge__(self, other):
        return self.y >= other.y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

