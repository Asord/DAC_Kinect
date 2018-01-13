# coding: utf8
from Manager.KinectManager import KinectManager
from Drawable.SnowGenerator import SnowGenerator
from Drawable.BallInteractive import BallInteractive
from Utilities.globals import Globals

from pygame import init, time, display, Surface, transform, event as pygEvent, quit as pygQuit
from pygame import HWSURFACE, DOUBLEBUF, QUIT, FULLSCREEN, K_ESCAPE, KEYDOWN, K_SPACE
from pygame.font import SysFont
from pygame.image import load

from os.path import join as path_join

if 'Debug' in Globals:
    FULLSCREEN = 0


class MainWindow:

    def __init__(self):
        # initialisation du moteur PyGames
        init()

        # Police pour l'information des FPS inscreen (debug)
        self._font = SysFont('System', 20)

        # Récupère la résolution de l'écran
        display_info = display.Info()
        resolution = (display_info.current_w, display_info.current_h)

        # Crée une fenettre graphique avec les informations nécessaires
        self._screen = display.set_mode(
            resolution,
            FULLSCREEN | HWSURFACE | DOUBLEBUF,
            32
        )

        # Définie le titre de la fenètre
        display.set_caption("Kinect V2 TP DAC")

        # Boolean qui devient True quand on quite le programme
        self._done = False

        # Variable contenant l'horloge d'éxécution du programme (pour définir un nombre limité de FPS)
        self._clock = time.Clock()

        # Crée un KinectManager qui se chargera de l'intéraction avec la Kinect 2
        self._KinectManager = KinectManager()

        # Charge en mémoire les deux textures de balle et d'explosion de balle
        self._ballTex = load(path_join('Resources', 'ball.png'))
        self._explosionTex = load(path_join('Resources', 'explosion.png'))

        # Crée les 2 objects d'intéraction (neige et balle)
        self._snow = SnowGenerator(self._KinectManager)  # TODO: send KM not Runtime
        self._ball = BallInteractive(self._KinectManager, self._ballTex, self._explosionTex)

        # Crée une surface de dessin pour afficher les différents éléments graphiques
        self._frame_surface = Surface(self._KinectManager.size, 0, 32)

        # défini le mode d'intéraction par défaut
        self._mode = 'Snow'  # | 'Ball'

    # affichage des FPS
    def _showFPS(self):

        # Affiche les fps dans le coins haut gauche
        self._screen.blit(self._font.render("fps: " + str(self._clock.get_fps()), 1, (255, 255, 255)), (20, 20))

    def _check_resize(self):
        ratio = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
        target_height = int(ratio * self._screen.get_width())
        return transform.scale(self._frame_surface, (self._screen.get_width(), target_height))

    # boucle d'execution principale
    def mainloop(self):

        # tant que l'application n'est pas marqué comme devant se fermer
        while not self._done:

            # récupération des événements de PyGames
            for event in pygEvent.get():

                # si l'événement est de type "QUIT" alors on flag self._done comme Vrai
                if event.type == QUIT:
                    self._done = True

                # sinon si l'événement est la touche 'escape' alors envoyer l'évenement quitter à la fenetre
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygQuit(); return

                    # si la touche est la barre 'espace' alors changer de mode d'intéraction
                    elif event.key == K_SPACE:
                        self._mode = 'Ball' if self._mode == 'Snow' else 'Snow'

            # Update window size and fps in-screen informations
            self._screen.blit(self._check_resize(), (0, 0))

            # Afficher les FPS (si débug)
            if 'Debug' in Globals: self._showFPS()

            # Dessiner les éléments de Kinect (image de la caméra, et body si débug)
            self._KinectManager.draw_color_frame(self._frame_surface)
            if "Debug" in Globals: self._KinectManager.draw_body(self._frame_surface, (255, 255, 0))

            # Si la colorFrame est disponible, alors la Kinect est bien lancé, alors récupération du premier body
            if self._KinectManager.colorFrameReady:
                body = self._KinectManager.get_first_body()

                # si il existe bien un body alors executer le script d'intéraction correspondant au mode
                if body is not None:
                    if self._mode == 'Snow': self._snow.draw(self._frame_surface)
                    elif self._mode == 'Ball': self._ball.draw(self._frame_surface)

            # mettre a jour les nouvelles informations de dessin
            display.flip()

            # défini la limite à 60 fps (par défaut)
            self._clock.tick(60)

        # ferme la fenètre
        pygQuit()