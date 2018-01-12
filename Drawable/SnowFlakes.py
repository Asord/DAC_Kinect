from Drawable import drawable
from Utilities.Vector import Vector2

from random import randint
from pygame import draw

class Snowflakes(drawable):

    def __init__(self, bound):
        # Vecteur de position du flocon de neige ainsi qu'un entier de taille (rayon)
        self.pos = Vector2.randValue((0, bound[0]), (1, 2))
        self.size = randint(10, 25)

        # Vecteur de transformation (mouvement) du flocon, généré aléatoirement entre x[-2, 2[ et y[1, 5[
        self._transform = Vector2.randValue((-2, 2), (1, 5))

        # Taille de la zone de jeu (x,y)
        self._bound = bound

        # couleur par défaut d'un flocon de neige
        self.color = (255, 255, 255)

    # fonction de mise à jour appelé si le flocon n'a pas de collision avec une surface
    def update(self, bound, bodyParts):

        # metre à jour la position et la zone de jeu (en cas de changement de taille de l'écran)
        self.pos += self._transform
        self._bound = bound

    def draw(self, surface):

        # fonction de dessin appelé dans la fonction draw() du générateur de neige
        draw.circle(surface, self.color, self.pos.toTuple(), self.size, 0)

    def isOutside(self):

        # détècte si le flocon est dans une position extérieure à l'écran
        # retourne true si il est en dehors, false sinon
        if self.pos.x < 0 or self.pos.x > self._bound[0]:
            return True
        if self.pos.y < 0 or self.pos.y > self._bound[1]:
            return True
        return False