from Drawable import drawable
from Drawable.SnowFlakes import Snowflakes

from Utilities.Vector import Vector2

from Manager.BodyPart import BodyPart
from Manager.KinectManager import skeleton_bones, volume_bones, circle_joints

class SnowGenerator(drawable):

    def __init__(self, kinectManager, max_elements = 800):
        # récupère l'instance du KinectManager
        self._kinect = kinectManager

        # définie la limite d'éléments à créer
        self._max_elements = max_elements

        # stock les flocons de neige et les éléments volumineux du premier body
        self._snowflakes = []
        self._BodyParts = []
        self._circleParts = {}

    # methode d'intéraction principale
    def update(self, bound):

        # pour tous les flocons de neige présents
        for snowflake in self._snowflakes:

            # par défaut ils ne sont pas en collision avec le body
            hasCollide = False

            # pour tous les éléments volumineux du corps
            for part in self._BodyParts:

                # si la différence x des 2 points de l'os est compris entre -100 et 100 (si l'angle est trop vertical)
                # on passe a l'élément volumineux suivant
                if -100 < part.vect.x < 100:
                    continue

                # si le flocon est dans pas dans les environs de l'os on passe à l'élément volumineux suivant
                if (snowflake.pos.y + 150 < part.min_y or
                    snowflake.pos.y - 150 > part.max_y or
                    snowflake.pos.x + 150 < part.min_x or
                    snowflake.pos.x - 150 > part.max_x ):
                    continue

                # si le flocon est à la position d'un des points de l'os alors
                # on le marque comme en collision et on termine la boucle
                if (part.upper_line_start == snowflake.pos or
                    part.upper_line_end == snowflake.pos):
                    hasCollide = True
                    break

                # si toutes les conditions précédantes sont passées, alors
                # on calcule la colision entre part et le flocon
                # si ce dernier est en collision alors on le marque comme tel et on termine la boucle
                if part.isCollide(snowflake):
                    hasCollide = True
                    break

            # si aucune collision n'à été détécté
            if not hasCollide:
                # pour tous les éléments circulaires du body
                for name, data in self._circleParts.items():

                    # si le flocon de neige ne se trouve pas dans les environs du cercle on passe au suivant
                    if (snowflake.pos.y + 150 < data[0].y or
                        snowflake.pos.y - 150 > data[0].y or
                        snowflake.pos.x + 150 < data[0].x or
                        snowflake.pos.x - 150 > data[0].x):
                        continue

                    # sinon on récupère le vecteur entre le centre de l'élément circulaire et le flocon
                    vect = Vector2.fromPoints(snowflake.pos, data[0])

                    # on calcule sa longeur
                    vect_len = vect.len()

                    # on calcule la taille cumulé des 2 cercles
                    circles_size = snowflake.size + data[1]

                    # si le flocon sur la limite du cercle de l'élément circulaire alors on le marque comme en collision
                    if (circles_size - 20 <= vect_len <= circles_size and
                        vect.y > 0):
                        hasCollide = True
                        break

            # si il n'y a pas de collision on met à jour le flocon (faire tomber)
            if not hasCollide:
                snowflake.update(bound, self._BodyParts)

            # si le flocon est en dehors de la zone de l'écran alors on le supprime
            if snowflake.isOutside():
                self._snowflakes.remove(snowflake)

        # si le nombre maximale des flocons n'est pas atteins alors on en crée 3 de plus
        if len(self._snowflakes) < self._max_elements:
                self._snowflakes.append(Snowflakes(bound))
                self._snowflakes.append(Snowflakes(bound))
                self._snowflakes.append(Snowflakes(bound))

    # fonction de dessin
    def draw(self, surface):

        # met à jour le body
        self._updateBodyPart()

        # appèle la fonction principale (met à jour l'intéraction)
        self.update(surface.get_size())

        # dessine tous les flocons
        for snowflake in self._snowflakes:
            snowflake.draw(surface)

    # mise à jour des éléments volumineux du corps
    def _updateBodyPart(self):

        # récupère le premier body trouvé
        body = self._kinect.firstBody

        # récupère les points dans l'espace de la caméra
        joints_points = self._kinect.body_joints_to_color_space(body.joints)

        # si il n'existe pas encore d'élements volumineux alors les créer
        if len(self._BodyParts) == 0:
            self._createBodyParts(joints_points)

        else:
            # pour tous les id des os du body
            for bone_id in range(len(volume_bones)):

                # récupère l'os correspondant
                bone = skeleton_bones[volume_bones[bone_id]]

                # si l'une des coordonnée de l'un des points de l'os est -inf alors on passe au suivant
                if (joints_points[bone[0]].x == float("-inf") or
                    joints_points[bone[0]].y == float("-inf") or
                    joints_points[bone[1]].x == float("-inf") or
                    joints_points[bone[1]].y == float("-inf")):
                    continue

                # sinon on convertie les points Kinect en points Vector2
                start_pt = Vector2.fromKinectPoint(joints_points[bone[0]])
                end_pt = Vector2.fromKinectPoint(joints_points[bone[1]])

                # si les points sont différents alors on met à jours la position de l'élément volumineux
                if start_pt != end_pt:
                    self._BodyParts[bone_id].update(start_pt, end_pt)

        # pour tous les éléments circulaires
        for name, data in circle_joints.items():

            # si l'une des coordonnée de l'élément circulaire est -inf on passe au suivant
            if (joints_points[data[0]].x == float("-inf") or
                joints_points[data[0]].y == float("-inf")):
                continue

            # on convertie le point Kinect en point Vector2
            point = Vector2.fromKinectPoint(joints_points[data[0]])

            # met à jour le cercle
            self._circleParts[name] = (point, data[1])

    # crée les parties volumineuses
    def _createBodyParts(self, joints_points):

        # pour tous les os du skeleton
        for bone in volume_bones:
            bone = skeleton_bones[bone]

            # si l'une des coordonnée de l'un des points de l'os est -inf on passe a la partie suivante
            if (joints_points[bone[0]].x == float("-inf") or
                joints_points[bone[0]].y == float("-inf") or
                joints_points[bone[1]].x == float("-inf") or
                joints_points[bone[1]].y == float("-inf")):
                continue

            # on convertie les points Kinect en points Vector2
            start_pt = Vector2.fromKinectPoint(joints_points[bone[0]])
            end_pt = Vector2.fromKinectPoint(joints_points[bone[1]])

            # si les 2 points sont différents alors on peux ajouter la partie volumineuse à la liste
            if start_pt != end_pt:
                self._BodyParts.append( BodyPart(start_pt, end_pt, 40) )