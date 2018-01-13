from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime

from Utilities.Vector import Vector2
from Manager.BodyPart import BodyPart
from Utilities.globals import Globals

from pygame import draw
from ctypes import memmove

skeleton_bones = {
    'Head': (PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
    'Neck': (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
    'Torso': (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),
    'Pelvis': (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
    'ShoulderRight': (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),
    'ShoulderLeft': (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
    'HipRight': (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),
    'HipLeft': (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),

    # Right Arm
    'HumerusRight': (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight),
    'RadiusRight': (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
    'CarpalsRight': (PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight),
    'HandRight': (PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight),
    'ThumpRight': (PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight),

    # Left Arm
    'HumerusLeft': (PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft),
    'RadiusLeft': (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
    'CarpalsLeft': (PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft),
    'HandLeft': (PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft),
    'ThumpLeft': (PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft),

    # Right Leg
    'FemurRight': (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight),
    'TibiaRight': (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight),
    'FootRight': (PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight),

    # Left Leg
    'FemurLeft': (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),
    'TibiaLeft': (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft),
    'FootLeft': (PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)
}

volume_bones = [
    'ShoulderRight', 'ShoulderLeft',
    'HumerusRight', 'HumerusLeft',
    'RadiusRight', 'RadiusLeft',
    'CarpalsRight', 'CarpalsLeft',
]

circle_joints = {
    'Head': (PyKinectV2.JointType_Head, 75)
}

class KinectManager:

    def __init__(self):

        # buffer gardant en mémoire la dernière image récupéré de la Kinect
        self._buffer = None

        # Instance de le Kinect
        self._kinect = PyKinectRuntime.PyKinectRuntime( PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body )

        # Variable stockant les informations de la dimention du flux vidéo de la Kinect
        self.size = (self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height)

        # Boolean si la Kinect est prètes à diffuser la vidéo
        self.colorFrameReady = False

        # Variable stockant le premier body trouvé
        self.firstBody = None

        # Variable stockant la position et l'état des 2 mains
        self.firstBodyHands = [] # format: [(point, state), (point, state)]

        # Liaison d'une methode de PyKinect a KinectManager
        self.body_joints_to_color_space = self._kinect.body_joints_to_color_space


    # récupère le premier body trouvé
    def get_first_body(self):

        # si il n'y a pas de nouveau body alors retourne l'encien body trouvé
        if  not self._kinect.has_new_body_frame(): return self.firstBody

        # pour tous les bodies trouvés
        for body in self._kinect.get_last_body_frame().bodies:

            # si le body est traqué alors met à jour le firstBody et le retourne
            if body.is_tracked:
                self.firstBody = body
                return body

        # Sinon retourne None
        self.firstBody = None
        return None

    # dessine le body trouvé
    def draw_body(self, frame_surface, color=(255, 0, 0)):

        # Si nous ne somme pas en mode Débug alors on n'execute pas la methode
        if not 'Debug' in Globals: return

        # met à jour et récupère le premier body trouvé, si il est inexistant alors on n'execute pas la methode
        body = self.get_first_body()
        if body is None: return

        # récupère la liste des joints du body
        joints = body.joints

        # Convertie les points dans le repère de la caméra
        joint_points = self._kinect.body_joints_to_color_space(joints)

        # pour tous les os du skeleton
        for name, bone in skeleton_bones.items():

            # récupération des joints
            joint_0 = bone[0]
            joint_1 = bone[1]

            # récupération des états de tracking des joints
            joint_0_State = joints[joint_0].TrackingState
            joint_1_State = joints[joint_1].TrackingState

            # si 1 des 2 joints n'est pas traqué alors on passe aux suivants
            if (joint_0_State == PyKinectV2.TrackingState_NotTracked or
                joint_1_State == PyKinectV2.TrackingState_NotTracked):
                continue

            # si les 2 joints ne sont pas correctement traqué alors on passe aux suivants
            if (joint_0_State == PyKinectV2.TrackingState_Inferred and
                joint_1_State == PyKinectV2.TrackingState_Inferred):
                continue

            # si l'un des points à pour coordonnée une valeur -inf alors on passe aux joints suivants
            if (joint_points[joint_0].x == float("-inf") or
                joint_points[joint_0].y == float("-inf") or
                joint_points[joint_1].x == float("-inf") or
                joint_points[joint_1].y == float("-inf")):
                continue

            # Conversion des 2 points Kinect en points Vector2
            start_pt = Vector2.fromKinectPoint(joint_points[joint_0])
            end_pt = Vector2.fromKinectPoint(joint_points[joint_1])

            # si les 2 points sont différents
            if start_pt != end_pt:

                # si le nom de l'os n'est pas dans la liste des os à considérer comme des volumes
                # on les déssinent comme une ligne
                if not name in volume_bones:
                    draw.line(frame_surface, color, start_pt.toTuple(), end_pt.toTuple(), 5)
                else: # sinon on les dessine comme des os volumineux
                    BodyPart.drawForm(frame_surface, color, start_pt, end_pt, 40, 5)

        # pour tous les joints à considérer comme center de cercles (pour la tête principalement)
        for name, data in circle_joints.items():

            # si le point à pour coordonnée une value -inf alors on passe au point suivant
            if (joint_points[data[0]].x == float("-inf") or
                joint_points[data[0]].y == float("-inf")):
                continue

            # conversion du point Kinect en point Vector2
            point = Vector2.fromKinectPoint(joint_points[data[0]])

            # Affiche le cercle en fonction du point de centre 'point' et de sa dimention
            draw.circle(frame_surface, color, point.toTuple(), data[1], 5)

        # calcule et affiche les états des mains
        self._drawHandsState(frame_surface, joint_points)

    # Calcule et affiche les états des mains
    def _drawHandsState(self, frame_surface, joint_points):

        # Récupère les points des 2 mains
        right_point = joint_points[PyKinectV2.JointType_HandRight]
        left_point = joint_points[PyKinectV2.JointType_HandLeft]

        # si l'une des coordonnées de l'une des main est -inf alors on retourne
        if (right_point.x == float("-inf") or
            right_point.y == float("-inf") or
            left_point.x == float("-inf") or
            left_point.y == float("-inf")):
            return

        # sinon on convertie les points Kinect en points Vector2
        right_hand_pos = Vector2.fromKinectPoint(right_point)
        left_hand_pos = Vector2.fromKinectPoint(left_point)

        # on récupère l'état des 2 mains
        right_hand_state = self.firstBody.hand_right_state
        left_hand_state = self.firstBody.hand_left_state

        # on définie la couleur de la main droite selon son état
        if right_hand_state == PyKinectV2.HandState_Closed:
            right_color = (255, 0, 0)
        elif right_hand_state == PyKinectV2.HandState_Open:
            right_color = (0, 255, 0)
        elif right_hand_state == PyKinectV2.HandState_Lasso:
            right_color = (0, 0, 255)
        else:
            right_color = (255, 255, 255)

        # on définie la couleur de la main gauche selon son état
        if left_hand_state == PyKinectV2.HandState_Closed:
            left_color = (255, 0, 0)
        elif left_hand_state == PyKinectV2.HandState_Open:
            left_color = (0, 255, 0)
        elif left_hand_state == PyKinectV2.HandState_Lasso:
            left_color = (0, 0, 255)
        else:
            left_color = (255, 255, 255)

        # on dessine les 2 cercles des mains
        draw.circle(frame_surface, right_color, right_hand_pos.toTuple(), 50, 0)
        draw.circle(frame_surface, left_color, left_hand_pos.toTuple(), 50, 0)

    # récupère les données caméra de la Kinect
    def draw_color_frame(self, target_surface):

        # si la Kinect a une nouvelle frame
        if self._kinect.has_new_color_frame():

            # on défini la condition ready
            self.colorFrameReady = True

            # on enregistre dans le buffer de la vidéo la nouvelle frame
            self._buffer = self._kinect.get_last_color_frame()

            # on lock la surface cible
            target_surface.lock()

            # on transfert les données du buffer dans la surface
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            memmove(address, self._buffer.ctypes.data, self._buffer.size)

            # on libère la surface cible
            target_surface.unlock()

    def getFirstBodyHandsPos(self):
        # met à jour et récupère le premier body trouvé, si il est inexistant alors on n'execute pas la methode
        body = self.get_first_body()
        if body is None: return -1, -1, -1, -1

        # récupère la liste des joints du body
        joints = body.joints

        # Convertie les points dans le repère de la caméra
        joint_points = self._kinect.body_joints_to_color_space(joints)
        # Récupère les points des 2 mains
        right_point = joint_points[PyKinectV2.JointType_HandRight]
        left_point = joint_points[PyKinectV2.JointType_HandLeft]

        # si l'une des coordonnées de l'une des main est -inf alors on retourne
        if (right_point.x == float("-inf") or
            right_point.y == float("-inf") or
            left_point.x == float("-inf") or
            left_point.y == float("-inf")):
            return -1, -1, -1, -1

        # sinon on convertie les points Kinect en points Vector2
        right_hand_pos = Vector2.fromKinectPoint(right_point)
        left_hand_pos = Vector2.fromKinectPoint(left_point)

        # on récupère l'état des 2 mains
        right_hand_state = self.firstBody.hand_right_state
        left_hand_state = self.firstBody.hand_left_state

        return right_hand_pos, right_hand_state, left_hand_pos, left_hand_state


    # getter du KinectRuntime
    def getKinect(self):
        return self._kinect

    # destructeur du manager chargé de fermer l'accès à la Kinect
    def __del__(self):
        self._kinect.close()