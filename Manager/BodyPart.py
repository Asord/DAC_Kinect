from Utilities.globals import Globals
from Utilities.Vector import Vector2

from Drawable import drawable
from pygame import draw

class BodyPart(drawable):

    def __init__(self, pointA, pointB, size):

        self.size = size

        self._create(pointA, pointB)

    def _create(self, pointA, pointB):

        self.pA = pointA
        self.pB = pointB

        self.vect = Vector2.fromPoints(self.pA, self.pB)

        _tmpA = self.vect.resize(self.size)

        if self.vect.x < 0:
            _startA = self.pA + _tmpA.rad_rotate(0.5)
            _startB = self.pA + _tmpA.deg_rotate(-0.5)
        else:
            _startA = self.pA + _tmpA.rad_rotate(-0.5)
            _startB = self.pA + _tmpA.deg_rotate(0.5)

        if _startA < _startB:
            self.upper_line_start = _startA
        else:
            self.upper_line_start = _startB

        self.upper_line_end = self.upper_line_start + self.vect

        if self.vect.x > 0:
            self.max_x = self.upper_line_end.x
            self.min_x = self.upper_line_start.x
        else:
            self.max_x = self.upper_line_start.x
            self.min_x = self.upper_line_end.x

        if self.vect.y > 0:
            self.max_y = self.upper_line_end.y
            self.min_y = self.upper_line_start.y
        else:
            self.max_y = self.upper_line_start.y
            self.min_y = self.upper_line_end.y


        _amplitude = self.vect.projectOn(Vector2(1, 0))
        self.projected_x = Vector2(1, 0).resize(_amplitude)

    @staticmethod
    def drawForm(surface, color, pointA, pointB, size, line_size):
        if not 'Debug' in Globals: return

        new = BodyPart(pointA, pointB, size)
        new.draw(surface, color, line_size)

    def draw(self, surface, color=(255, 0, 0), line_size=1):
        if not 'Debug' in Globals: return

        draw.circle(surface, color, self.pA.toTuple(), self.size, line_size)

        self.vect.draw(surface, self.upper_line_start, (255, 0, 0))
        self.projected_x.draw(surface, self.pA)

        return

    def isCollide(self, snowflake):
        startToBall = Vector2.fromPoints(self.upper_line_start, snowflake.pos)
        endToBall = Vector2.fromPoints(self.upper_line_start + self.vect, snowflake.pos)

        normal = startToBall.rad_rotate(-0.5)
        proj = self.vect.projectOn(normal)

        if (-self.size < proj <= snowflake.size and
            self.projected_x.dot(startToBall) > 0 and
            self.projected_x.dot(endToBall) < 0):
            return True

        return False

    def update(self, pointA, pointB):
        if pointA != self.pA or pointB != self.pB:
            self._create(pointA, pointB)
