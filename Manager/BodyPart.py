from Utilities.globals import Globals
from Utilities.Vector import Vector2

from Drawable import drawable
from pygame import draw

class BodyPart(drawable):

    def __init__(self, pointA, pointB, size):

        # définie la taille (épaisseur) de la partie volumineuse du corps
        self.size = size

        # créer la partie volumineuse du point a au point b
        self._create(pointA, pointB)

    def _create(self, pointA, pointB):

        # stockage des points de la partie
        self.pA = pointA
        self.pB = pointB

        # création du vecteur de A vers B
        self.vect = Vector2.fromPoints(self.pA, self.pB)

        # vecteur temporaire ayant la même direction que vect mais avec la taille de size
        _tmpA = self.vect.resize(self.size)

        # détermine la rotation nécéssaire selon la direction du vecteur (voire compte rendu pour plus d'informations)
        if self.vect.x < 0:
            _startA = self.pA + _tmpA.rad_rotate(0.5)
            _startB = self.pA + _tmpA.deg_rotate(-0.5)
        else:
            _startA = self.pA + _tmpA.rad_rotate(-0.5)
            _startB = self.pA + _tmpA.deg_rotate(0.5)

        # détermination du point suppérieur
        if _startA < _startB:
            self.upper_line_start = _startA
        else:
            self.upper_line_start = _startB

        # détermination du point de fin de la ligne suppérieur
        self.upper_line_end = self.upper_line_start + self.vect

        # détermination des points suppérieurs max et min en x et en y
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

        # calcule du projeté du vecteur sur l'axe x
        _amplitude = self.vect.projectOn(Vector2(1, 0))
        self.projected_x = Vector2(1, 0).resize(_amplitude)

    @staticmethod
    def drawForm(surface, color, pointA, pointB, size, line_size):
        # fonction débug uniquement: crée et dessine un objet volumineux
        if not 'Debug' in Globals: return

        new = BodyPart(pointA, pointB, size)
        new.draw(surface, color, line_size)

    def draw(self, surface, color=(255, 0, 0), line_size=1):
        # fonction débug uniquement: dessine l'objet volumineux actuel
        if not 'Debug' in Globals: return

        # dessine le cercle ce centre A et de taille size
        draw.circle(surface, color, self.pA.toTuple(), self.size, line_size)

        # dessine le vecteur suppérieur de l'objet ainsi que son projeté sur l'axe x
        self.vect.draw(surface, self.upper_line_start, (255, 0, 0))
        self.projected_x.draw(surface, self.pA)


    def isCollide(self, snowflake):
        # détecte les collisions entre une sphère et la droite représentative de la partie suppérieur de l'objet

        # détermine le vecteur entre A et le flocon, et entre B et le flocon
        startToBall = Vector2.fromPoints(self.upper_line_start, snowflake.pos)
        endToBall = Vector2.fromPoints(self.upper_line_start + self.vect, snowflake.pos)

        # calcule de la normale du vecteur [A; flocon] ainsi que le projeté du vecteur sur cette normale
        normal = startToBall.rad_rotate(-0.5)
        proj = self.vect.projectOn(normal)

        # si je projeté à une taille comprise entre la taille de l'objet et du flocon
        # que le produit scalaire du projeté en x est du vecteur [A; flocon] est > 0 et
        # que le produit scalaire du projeté en x du vecteur [B; flocon] est < 0
        # Donc si le flocon se trouve proche et au dessus de la ligne (voire compte rendu), il est en collision
        # alors retourner True
        if (-self.size < proj <= snowflake.size and
            self.projected_x.dot(startToBall) > 0 and
            self.projected_x.dot(endToBall) < 0):
            return True

        # sinon la collision n'est pas existante
        return False

    # si l'objet volumineux à besoins d'être mis à jour, alors execute la methode _create()
    def update(self, pointA, pointB):
        if pointA != self.pA or pointB != self.pB:
            self._create(pointA, pointB)
