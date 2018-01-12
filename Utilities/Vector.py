from math import sqrt, radians, pi
from math import sin as math_sin, cos as math_cos

from Utilities.globals import Globals

from pygame import draw

class Vector2:
    # Vector2 gère un vecteur de dimention 2 représentant des vecteurs, et des points d'un espace 2D
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def fromKinectPoint(cls, ColorSpacePoint):
        # Créer un Vector2 depuis un point PyKinect
        return cls(ColorSpacePoint.x, ColorSpacePoint.y)

    @classmethod
    def fromTuple(cls, tu):
        # Créer un Vector2 depuis un tuple
        return cls(tu[0], tu[1])

    @classmethod
    def zero(cls):
        # Créer un Vector2 de données (0,0)
        return cls(0, 0)

    @staticmethod
    def isVector(obj):
        # Détermine si obj est de type Vector2
        return type(obj) is Vector2

    @staticmethod
    def toRect(vect1, vect2):
        # Créer un tuple de tuple de vecteurs
        # D'ordinaire, vect1 est un point, et vect2 une dimention
        # Donc on créer ((P.x, P.y), (width, height))
        return vect1.toTuple(), vect2.toTuple()

    @classmethod
    def randValue(cls, x=(0, 10), y=(0, 1)):
        # Créer un point de position aléatoire définie par 2 tuples en paramètres
        from random import randrange
        return cls(randrange(x[0], x[1]), randrange(y[0], y[1]))

    @classmethod
    def fromPoints(cls, pointA, pointB):
        # Créer un vecteur Vector2 depuis 2 points Vector2
        return cls(pointB.x - pointA.x, pointB.y - pointA.y)

    def toTuple(self):
        # Retourne une représentation en tuple du Vector2 (uniquement en entier)
        return int(self.x), int(self.y)

    def resize(self, new_size):
        # Redimentionne un Vector2 selon une taille précisé

        # Calcule de la longeur actuelle du vecteur
        len = self.len()

        # Si la longeur Actuelle, alors on défini son ratio de transformation comme sa taille demandé
        if len < 1:
            _ratio = new_size
        else: # sinon on calcule son ratio
            _ratio = new_size / len
        return self.ratio(_ratio) # et on retourne le vecteur redimentionnée

    def ratio(self, value):
        # Crée un nouveau vecteur redimentionné selon un ratio
        return Vector2(self.x * value, self.y * value)

    def deg_rotate(self, angle):
        # calcule la rotation en degré d'un vecteur (par transformation en radian)
        return self.rad_rotate(radians(angle % 360))

    def rad_rotate(self, angle):
        # Calcule de la rotation d'un vecteur en radian

        # calcule des valeurs sin et cos de l'angle
        sin = math_sin(pi * angle)
        cos = math_cos(pi * angle)

        # rotation du vecteur
        new_x = (cos * self.x) - (sin * self.y)
        new_y = (sin * self.x) + (cos * self.y)
        return Vector2(new_x, new_y)

    def projectOn(self, other):
        # calcule de la projection (produit scalaire de la norme)
        return self.dot(other.normalize())

    def dot(self, other):
        # calcule du produit scalaire
        return (self.x * other.x) + (self.y * other.y)

    def normalize(self):
        # calcule de la norme du vecteur
        x = self.x/self.len()
        y = self.y/self.len()
        return Vector2(x, y)

    def draw(self, surface, start_pt, color=(0, 255, 0), line_size=5):
        # fonction débug uniquement: dessine le vecteur selon un point de départ
        if not 'Debug' in Globals: return

        end_pt = start_pt + self
        draw.line(surface, color, start_pt.toTuple(), end_pt.toTuple(), line_size)

    def len(self):
        # calcule de la longeur du vecteur (pytagore)
        return sqrt(self.x **2 + self.y ** 2)

    def __len__(self):
        # operateur de longeur ( utilisé avec len(object) )
        return self.len()

    def __sub__(self, other):
        # opérateur soustraction binaire
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        # opérateur addition binaire
        return Vector2(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        # operateur équalité
        return self.x == other.x and self.y == other.y

    def __iadd__(self, other):
        # operateur addition affectation
        self.x += other.x
        self.y += other.y
        return self

    def __ne__(self, other):
        # operateur différent
        return self.x != other.x or self.y != other.y

    def __gt__(self, other):
        # opérateur plus grand que (pour le hauteur)
        return self.y > other.y

    def __lt__(self, other):
        # operateur plus petit que (pour la hauteur)
        return self.y < other.y

    def __le__(self, other):
        # opérateur plus petit ou égale (pour la hauteur)
        return self.y <= other.y

    def __ge__(self, other):
        # opérateur plus grand ou égale (pour la hauteur)
        return self.y >= other.y

    def __str__(self):
        # operateur représentation en string (utilise dans un string ou avec str(object))
        return '({}, {})'.format(self.x, self.y)