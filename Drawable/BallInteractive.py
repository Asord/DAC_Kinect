from Drawable import drawable

from Utilities.Vector import Vector2

from pygame import transform

from __lib.PyKinectV2 import JointType_HandLeft, JointType_HandRight
from __lib.PyKinectRuntime import TrackingState_NotTracked, TrackingState_Inferred
from __lib.PyKinectRuntime import HandState_Closed, HandState_NotTracked

class BallInteractive(drawable):

    def __init__(self, kinectManager, ballTex, explosionTex):

        # manager des communications avec la Kinect
        self._kinect = kinectManager

        # tableau de 2 Vecteur2 de positions des mains
        self.hands = []

        # rectangle invisible contenant la zone de dessin du ballon
        self._ballRect = ((0, 0), (0, 0))

        # Vecteur entre les 2 mains
        self._handsVector = Vector2.zero()

        # point central de l'image
        self._center = Vector2.zero()

        # cache de la texture de la balle
        self._texCache = None
        # cache de la texture de l'explosion
        self._explosionCache = None

        # textures originales (non redimentionnées)
        self._ballTex = ballTex
        self._explosionTex = explosionTex

        # boolean si la balle est vérouillé au centre (si elle n'a pas été saisie virtuellement en fermant les mains)
        self._locked = False
        # boolean si l'explosion est en cours ou non accompagné du timer de l'explosion, sert à crée une animation
        self._explode = False
        self._explode_timer = 0

    # fonciton update appelé a chaque boucle d'interface
    def update(self, screen):

        # Effectue la mise a jour des positions des mains et test si le résultat est incorrecte (opperation échouée)
        if self._update_hands_pos() != 0:

            # dans le cas ou c'est échoué, si la balle n'est pas vérouillé alors
            if not self._locked:
                # création d'un vecteur de handVector(300; 300)
                self._handsVector = Vector2(300, 300)

                # récupération de la taille de l'écran et calcule du point centrale (taille/2)
                size = Vector2.fromTuple(screen.get_size())
                self._center = size.ratio(0.5)

                # calcule du coint suppérieur gauche d'un carré de 300x300 centré
                upperLeft = self._center + Vector2(-150, -150)

                # définition du rectangle de balle comme partant du coint suppérieur gauche et faisant 300x300 de taille)
                self._ballRect = (upperLeft.toTuple(), self._handsVector.toTuple())

                # redimentionnement de la texture de balle à la taille 300x300 et stockage dans le cache
                self._texCache = transform.scale(self._ballTex, self._handsVector.toTuple())

                # action du lock pour ne pas avoir à refaire ces oppérations tant que la balle de change pas d'état
                self._locked = True

        # si la balle est vérouillé alors on a pas plus d'oppérations à effectué
        if self._locked: return

        # sinon, si la balle n'est pas vérouillé mais qu'il n'existe pas de mains alors on arrête la procédure
        if len(self.hands) == 0: return

        # autrement, on récupère les coordonnées max et min en x et en y des points des mains
        y_min = min(self.hands[0].y, self.hands[1].y)
        y_max = max(self.hands[0].y, self.hands[1].y)
        x_min = min(self.hands[0].x, self.hands[1].x)
        x_max = max(self.hands[0].x, self.hands[1].x)

        # on crée un vecteur allant du y le plus haut et du x le plus à gauche
        # et on ajour 100 de hauteur (meilleur représentation)
        # on crée ensuite un vecteur allant du y le plus bas et du x le plus a droite
        # et on ajoute 100 en bas (meilleur représentation)
        # Cf: voire compte rendu pour plus de détails
        upperLeft  = Vector2(x_min, y_min) + Vector2(0, -100)
        lowerRight = Vector2(x_max, y_max) + Vector2(0, 100)

        # création du vecteur des mains ainsi que redimentionnement de la texture pour la stocker dans le cache
        self._handsVector = Vector2.fromPoints(upperLeft, lowerRight)
        self._texCache = transform.scale(self._ballTex, self._handsVector.toTuple())

        # si la taille d'une des valeur du vecteur est bien > 0 (normalement ça devrait toujours être la cas)
        # alors définire la zone de dessin de la balle comme démarant du point haut gauche et de taille du vecteur
        if self._handsVector.x > 0 and self._handsVector.y > 0:
            self._ballRect = (upperLeft.toTuple(), self._handsVector.toTuple())

    # methode de dessin de balle
    def draw(self, screen):

        # mise a jour des données
        self.update(screen)

        # si texCache existe bien (qu'une texture est bien disponible pour dessin)
        if self._texCache is not None:
            # si la balle n'est pas marqué comme explosant
            if not self._explode:
                # dessiner la balle
                screen.blit(self._texCache, self._ballRect)
            else:
                # non si la balle est marqué comme explosant, et que le timer est différent de 0 alors
                if self._explode_timer != 0:

                    # récupérer le rect d'explosion (rectangle de taille variable en fonction du timer)
                    rect = self._get_explosion_rect()

                    # redimention de la texture d'explosion et mise en cache, puis dessiner l'explosion
                    self._explosionCache = transform.scale(self._explosionTex, rect[1])
                    screen.blit(self._explosionCache, rect)

                    # décroissement du timer de 1
                    self._explode_timer -= 1
                else:
                    # sinon, si l'explosion est marqué comme vraie mais que le timer est à 0
                    # alors marquer l'explosion comme fausse
                    self._explode = False

    def _get_explosion_rect(self):
        # récupère le rectangle de l'explosion en fonction du temps
        # voire compte rendu pour plus de détails

        x = int(self._center.x - 150 // self._explode_timer)
        y = int(self._center.y - 150// self._explode_timer)
        vx = int(self._handsVector.x // self._explode_timer)
        vy = int(self._handsVector.y // self._explode_timer)
        return (x, y), (vx, vy)

    def _update_hands_pos(self):

        # récupère le premier body de la Kinect
        body = self._kinect.firstBody

        # récupérer les joints du body ainsi que leurs coordonnées dans l'espace de caméra de couleur
        joints = body.joints
        joint_points = self._kinect.body_joints_to_color_space(joints)

        # récupération de l'état de tracking des 2 mains
        leftHand_TrackState = joints[JointType_HandLeft].TrackingState
        rightHand_TrackState = joints[JointType_HandRight].TrackingState

        # récupération de l'état des 2 mains (lasso, ouvert, fermé, non référancé, inconnu)
        handsState = [body.hand_left_state, body.hand_right_state]

        # si les 2 mains ne sont pas tracké ou que l'une des 2 est hors zone on retourne 1 (non ref)
        if (leftHand_TrackState == TrackingState_NotTracked and  rightHand_TrackState == TrackingState_NotTracked or
            (leftHand_TrackState == TrackingState_Inferred or rightHand_TrackState == TrackingState_Inferred)):
            return 1

        # si l'une des coordonnée de l'un des points de la main est à -inf on retourne 1 (non ref)
        if (joint_points[JointType_HandLeft].x == float("-inf") or
            joint_points[JointType_HandLeft].y == float("-inf") or
            joint_points[JointType_HandRight].x == float("-inf") or
            joint_points[JointType_HandRight].y == float("-inf")):
            return 1

        # création des 2 points Vector2 depuis les points PyKinect
        leftPoint = Vector2.fromKinectPoint(joint_points[JointType_HandLeft])
        rightPoint = Vector2.fromKinectPoint(joint_points[JointType_HandRight])

        # si l'état de l'une des 2 mains est fermé (pas les 2 car difficultées de détection des mains proches du body)
        if handsState[0] == HandState_Closed or handsState[1] == HandState_Closed:

            # si la balle est locked
            if self._locked:
                # si les mains sont a environ 200 du centre (sur les bordures de la balle) alors on désactive le lock
                if (Vector2.fromPoints(leftPoint, self._center).len() <= 200 or
                    Vector2.fromPoints(rightPoint, self._center).len() <= 200):
                        self._locked = False

            # enregistrement des positions des mains
            self.hands = [leftPoint, rightPoint]

            # retourne 0 (réussite)
            return 0

        # sinon si l'état des 2 mains est non tracké
        # (si les mains sont trop proches du centre pour avoir un état identifié)
        elif handsState[0] == HandState_NotTracked and handsState[1] == HandState_NotTracked:

            # si la balle n'est pas marqué comme ayant explosé
            if not self._explode:

                # si la position des mains est très proche du centre (écrasement de la balle)
                if (Vector2.fromPoints(leftPoint, self._center).len() <= 150 or
                    Vector2.fromPoints(rightPoint, self._center).len() <= 150):
                    # marquer l'explosion comme vraie et définire le timer sur 30 (environ 1sec à 30fps)
                    self._explode = True
                    self._explode_timer = 30

            # retourner 2 (untracked)
            return 2