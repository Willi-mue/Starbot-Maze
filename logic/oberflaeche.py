import sys
from logic import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pygame
import ctypes


class main_application(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("bilder/icon.png"))
        # Setzen des Icons
        my_app_id = 'by_Müller_Willi.MyPacman.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

        self.setWindowTitle('Pacman_Python')

        self.hoehe = 1080
        self.breite = 1920
        self.hoehe_half = self.hoehe // 2
        self.breite_half = self.breite // 2
        self.resize(self.breite, self.hoehe)
        self.setMinimumSize(self.breite, self.hoehe)

        pygame.mixer.init()
        pygame.mixer.music.load("musik/Pac_man_theme_remix_By_Arsenic1987.mp3")
        # links:
        # https://www.youtube.com/watch?v=qtZ0hl-unM4
        # https://open.spotify.com/track/5Jt6qtZfj0YSHfFBJUyviK?si=MLYHvd74QM-Tp8Bz4UukUQ&nd

        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.02)

        self.lvl = 1

        self.tile_size = 25

        self.right = False
        self.down = False
        self.up = False
        self.left = False
        self.ani = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animation)
        self.speed = 80
        self.timer.start(self.speed)

        self.show_gameover = False
        self.show_gameover_count = 0

        self.lvl_complete = False
        self.hit_switch = False

        self.links_oben = QImage("bilder/links_oben.png")
        self.rechts_oben = QImage("bilder/rechts_oben.png")
        self.links_unten = QImage("bilder/links_unten.png")
        self.rechts_unten = QImage("bilder/rechts_unten.png")
        self.horizontal = QImage("bilder/horizontal.png")
        self.vertikal = QImage("bilder/vertikal.png")
        self.point = QImage("bilder/point.png")
        self.power_up = QImage("bilder/power_up.png")
        self.arcade = QImage("bilder/arcade.png")
        self.herz = QImage("bilder/herz.png")

        self.spieler_img = [QImage("bilder/player_idle.png"), QImage("bilder/player_left.png"),
                            QImage("bilder/player_right.png"), QImage("bilder/player_up.png"),
                            QImage("bilder/player_down.png"),
                            QImage("bilder/player_idle_hit.png"),
                            QImage("bilder/player_left_hit.png"), QImage("bilder/player_right_hit.png"),
                            QImage("bilder/player_up_hit.png"), QImage("bilder/player_down_hit.png"),
                            QImage("bilder/player_idle_hit2.png"),
                            QImage("bilder/player_left_hit2.png"), QImage("bilder/player_right_hit2.png"),
                            QImage("bilder/player_up_hit2.png"), QImage("bilder/player_down_hit2.png")
                            ]

        self.blue_ghost_img = ["bilder/geist_blau.png"]
        self.orange_ghost_img = ["bilder/geist_orange.png"]
        self.red_ghost_img = ["bilder/geist_rot.png"]
        self.purple_ghost_img = ["bilder/geist_lila.png"]

        geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
        geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
        geister.ghosts["ghost_red"].extend(self.red_ghost_img)
        geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)

        self.spieler_index = 0
        self.spieler_punkte = 0

        self.verschiebung_x = 200
        self.verschiebung_y = 150

    def animation(self):
        if spieler.life > 0:
            if self.ani:
                self.spieler_index = 0
                if spieler.imun < spieler.max_imun:
                    if spieler.imun % 4 == 0:
                        self.hit_switch = True
                    elif spieler.imun % 2 == 0:
                        self.hit_switch = False

                    if not self.hit_switch:
                        self.spieler_index = 5
                    else:
                        self.spieler_index = 10

                self.ani = False

            else:
                if self.left:
                    spieler.player_move(0, 0)
                    self.spieler_index = 1
                    if spieler.imun < spieler.max_imun:
                        if spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 6
                        else:
                            self.spieler_index = 11

                    spieler.player_move(-1, 0)
                    geister.move_ghost()
                    spieler.player_move(0, 0)

                    self.ani = True

                if self.right:
                    spieler.player_move(0, 0)
                    self.spieler_index = 2
                    if spieler.imun < spieler.max_imun:
                        if spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 7
                        else:
                            self.spieler_index = 12

                    spieler.player_move(1, 0)
                    geister.move_ghost()
                    spieler.player_move(0, 0)

                    self.ani = True

                if self.up:
                    spieler.player_move(0, 0)
                    self.spieler_index = 3
                    if spieler.imun < spieler.max_imun:
                        if spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 8
                        else:
                            self.spieler_index = 13

                    spieler.player_move(0, -1)
                    geister.move_ghost()

                    self.ani = True

                if self.down:
                    spieler.player_move(0, 0)
                    self.spieler_index = 4
                    if spieler.imun < spieler.max_imun:
                        if spieler.imun % 3 == 0:
                            self.hit_switch = True
                        elif spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 9
                        else:
                            self.spieler_index = 14

                    spieler.player_move(0, 1)
                    geister.move_ghost()
                    spieler.player_move(0, 0)

                    self.ani = True

            self.spieler_punkte = spieler.point
            self.lvl_complete = map_tiles.point_map_check()

            if self.lvl_complete:
                geister.ghosts = {"ghost_blue": [16, 18], "ghost_orange": [16, 16],
                                  "ghost_red": [14, 16], "ghost_purple": [16, 14]}

                geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
                geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
                geister.ghosts["ghost_red"].extend(self.red_ghost_img)
                geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)

                self.lvl_complete = False
                self.lvl += 1
                spieler.player_x = 16
                spieler.player_y = 24
                map_tiles.einlesen("../game/map.txt")
                self.right = False
                self.down = False
                self.up = False
                self.left = False

            self.update()
        else:
            self.show_gameover_count += 0.5
            if self.show_gameover and (self.show_gameover_count % 4 == 0):
                self.show_gameover = False
            elif not self.show_gameover and (self.show_gameover_count % 2 == 0):
                self.show_gameover = True

            self.update()

    def paintEvent(self, event):
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.black)
        painter = QPainter(self)
        painter.setPen(pen)

        painter.fillRect(QRect(0, 0, self.breite, self.hoehe), QColor("black"))

        pen.setColor(Qt.white)
        painter.setFont(QFont("times", 29))
        painter.setPen(pen)

        painter.drawText(self.breite - 800, self.hoehe - 850, "Level: " + str(self.lvl))

        if spieler.power_mode:
            painter.drawText(self.breite - 500, self.hoehe - 850, "Power: " + str(spieler.power_time))

        painter.setFont(QFont("times", 10))

        painter.drawText(100, self.hoehe - 50, "Game made by Willi Müller")
        painter.drawText(100, self.hoehe - 35, "Musik by Arsenic1987")

        painter.setFont(QFont("times", 29))

        painter.drawText(self.breite - 800, self.hoehe - 625, "Score: " + str(self.spieler_punkte))

        painter.drawText(self.breite - 800, self.hoehe - 735, "Life: ")

        painter.drawText(self.breite - 500, self.hoehe - 550, "Highscore")
        painter.drawLine(self.breite - 500, self.hoehe - 540, self.breite - 340, self.hoehe - 540)

        painter.setFont(QFont("times", 24))
        for i in range(10):
            # Highscore malen lassen
            painter.drawText(self.breite - 800, self.hoehe - 500 + (50 * i), str(i + 1) + ". ")
            painter.drawText(self.breite - 700, self.hoehe - 500 + (50 * i), str(score.text[i]))

        if spieler.life == 0 and self.show_gameover:
            painter.setFont(QFont("times", 60))
            painter.drawText(self.breite - 500, self.hoehe - 810, "GAME OVER")
            painter.setFont(QFont("times", 35))
            painter.drawText(self.breite - 470, self.hoehe - 720, "Press R to Restart")

        for i in range(spieler.life):
            painter.drawImage(QRect(self.breite - 700 + (100 * i), self.hoehe - 790, 80, 80), self.herz)

        pen.setColor(Qt.black)
        painter.setPen(pen)

        if spieler.life > 0:
            painter.drawImage(
                QRect((spieler.player_x * self.tile_size) + self.verschiebung_x, (spieler.player_y * self.tile_size)
                      + self.verschiebung_y, self.tile_size, self.tile_size),
                self.spieler_img[self.spieler_index])

        painter.drawImage(QRect(self.verschiebung_x, 0, self.breite - 400, self.verschiebung_y), self.arcade)

        for i in range(len(map_tiles.map_text)):
            for j in range(len(map_tiles.map_text[i])):
                if map_tiles.map_text[i][j] == "┌":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.links_oben)
                elif map_tiles.map_text[i][j] == "┐":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.rechts_oben)
                elif map_tiles.map_text[i][j] == "└":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.links_unten)
                elif map_tiles.map_text[i][j] == "┘":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.rechts_unten)
                elif map_tiles.map_text[i][j] == "─":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.horizontal)
                elif map_tiles.map_text[i][j] == "│":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.vertikal)
                elif map_tiles.map_text[i][j] == "@":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.power_up)
                elif map_tiles.map_text[i][j] == "•" or map_tiles.map_text[i][j] == "x":
                    painter.drawImage(QRect(0 + (j * self.tile_size) + self.verschiebung_x, 0 + (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.point)
                elif map_tiles.map_text[i][j] == " ":
                    pass

        for k in geister.ghosts:
            if spieler.power_mode and geister.ghost_imun[k]:
                painter.drawImage(QRect(0 + (geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x, 0 +
                                        (geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage("bilder/geist_imun"))

            elif spieler.power_mode:
                painter.drawImage(QRect(0 + (geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x, 0 +
                                        (geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage("bilder/geist_power"))

            else:
                painter.drawImage(QRect(0 + (geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x, 0 +
                                        (geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage(geister.ghosts[k][2]))

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self.left = True
            self.right = False
            self.down = False
            self.up = False
        if key == Qt.Key_Up:
            self.up = True
            self.down = False
            self.left = False
            self.right = False
        if key == Qt.Key_Down:
            self.up = False
            self.down = True
            self.left = False
            self.right = False
        if key == Qt.Key_Right:
            self.left = False
            self.right = True
            self.down = False
            self.up = False

        if key == Qt.Key_A:
            self.left = True
            self.right = False
            self.down = False
            self.up = False
        if key == Qt.Key_W:
            self.up = True
            self.down = False
            self.left = False
            self.right = False
        if key == Qt.Key_S:
            self.up = False
            self.down = True
            self.left = False
            self.right = False
        if key == Qt.Key_D:
            self.left = False
            self.right = True
            self.down = False
            self.up = False
        if key == Qt.Key_Escape:
            score.write_score(spieler.point)
            sys.exit()

        if (spieler.life == 0) and key == Qt.Key_R:
            geister.ghosts = {"ghost_blue": [16, 18], "ghost_orange": [16, 16],
                              "ghost_red": [14, 16], "ghost_purple": [16, 14]}

            geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
            geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
            geister.ghosts["ghost_red"].extend(self.red_ghost_img)
            geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)
            spieler.imun = spieler.max_imun
            spieler.player_x = 16
            spieler.player_y = 24
            score.write_score(spieler.point)
            spieler.point = 0
            self.lvl = 1
            spieler.life = 3
            map_tiles.einlesen("../game/map.txt")
            self.right = False
            self.down = False
            self.up = False
            self.left = False


def main():
    app = QApplication(sys.argv)
    application = main_application()
    #application.showFullScreen()
    application.show()
    sys.exit(app.exec_())


main()
