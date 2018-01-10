from Drawable import drawable

from Utilities.Vector import Vector2
from Utilities import test_or

from pygame import transform

from __lib.PyKinectV2 import JointType_HandLeft, JointType_HandRight
from __lib.PyKinectRuntime import TrackingState_NotTracked, TrackingState_Inferred
from __lib.PyKinectRuntime import HandState_Closed, HandState_NotTracked

class BallInteractive(drawable):

    def __init__(self, kinectManager, ballTex, explosionTex):

        self.hands = []

        self._kinect = kinectManager

        self._ballRect = ((0, 0), (0, 0))

        self._handsVector = Vector2.zero()
        self._center = Vector2.zero()

        self._texCache = None
        self._explosionCache = None

        self._ballTex = ballTex
        self._explosionTex = explosionTex

        self._locked = False
        self._explode = False
        self._explode_timer = 0

    def update(self, screen):

        if self._update_hands_pos() != 0:

            if not self._locked:
                self._handsVector = Vector2(300, 300)
                size = Vector2.fromTuple(screen.get_size())
                self._center = size.ratio(0.5)
                upperLeft = self._center + Vector2(-150, -150)
                self._ballRect = (upperLeft.toTuple(), self._handsVector.toTuple())
                self._texCache = transform.scale(self._ballTex, self._handsVector.toTuple())
                self._locked = True

        if self._locked: return

        if len(self.hands) == 0: return

        y_min = min(self.hands[0].y, self.hands[1].y)
        y_max = max(self.hands[0].y, self.hands[1].y)
        x_min = min(self.hands[0].x, self.hands[1].x)
        x_max = max(self.hands[0].x, self.hands[1].x)

        upperLeft  = Vector2(x_min, y_min) + Vector2(0, -100)
        lowerRight = Vector2(x_max, y_max) + Vector2(0, 100)

        self._handsVector = Vector2.fromPoints(upperLeft, lowerRight)
        self._texCache = transform.scale(self._ballTex, self._handsVector.toTuple())

        if self._handsVector.x > 0 and self._handsVector.y > 0:
            self._ballRect = (upperLeft.toTuple(), self._handsVector.toTuple())

    def draw(self, screen):

        self.update(screen)

        if self._texCache is not None:
            if not self._explode:
                screen.blit(self._texCache, self._ballRect)
            else:
                if self._explode_timer != 0:
                    rect = self._get_explosion_rect()
                    self._explosionCache = transform.scale(self._explosionTex, rect[1])
                    screen.blit(self._explosionCache, rect)
                    self._explode_timer -= 1
                else:
                    self._explode = False

    def _get_explosion_rect(self):
        x = int(self._center.x - 150 // self._explode_timer)
        y = int(self._center.y - 150// self._explode_timer)
        vx = int(self._handsVector.x // self._explode_timer)
        vy = int(self._handsVector.y // self._explode_timer)
        return (x, y), (vx, vy)

    def _update_hands_pos(self):

        body = self._kinect.firstBody

        joints = body.joints
        joint_points = self._kinect.body_joints_to_color_space(joints)

        leftHand_TrackState = joints[JointType_HandLeft].TrackingState
        rightHand_TrackState = joints[JointType_HandRight].TrackingState

        handsState = [body.hand_left_state, body.hand_right_state]

        if test_or(TrackingState_NotTracked, leftHand_TrackState, rightHand_TrackState):
            return 1

        if leftHand_TrackState == TrackingState_Inferred or rightHand_TrackState == TrackingState_Inferred:
            return 1

        if (joint_points[JointType_HandLeft].x == float("-inf") or
            joint_points[JointType_HandLeft].y == float("-inf") or
            joint_points[JointType_HandRight].x == float("-inf") or
            joint_points[JointType_HandRight].y == float("-inf")):
            return 1

        leftPoint = Vector2.fromKinectPoint(joint_points[JointType_HandLeft])
        rightPoint = Vector2.fromKinectPoint(joint_points[JointType_HandRight])

        if handsState[0] == HandState_Closed or handsState[1] == HandState_Closed:

            if self._locked:

                if (Vector2.fromPoints(leftPoint, self._center).len() <= 200 or
                    Vector2.fromPoints(rightPoint, self._center).len() <= 200):
                        self._locked = False

            self.hands = [leftPoint, rightPoint]

            return 0

        elif handsState[0] == HandState_NotTracked and handsState[1] == HandState_NotTracked:

            if not self._explode:

                if (Vector2.fromPoints(leftPoint, self._center).len() <= 150 or
                        Vector2.fromPoints(rightPoint, self._center).len() <= 150):
                    self._explode = True
                    self._explode_timer = 30

            return 2
