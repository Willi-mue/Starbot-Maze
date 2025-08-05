import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# import pygame
import ctypes

from io import open
import random


class highscore:

    def __init__(self, dir_highscore):
        self.save = dir_highscore
        self.file = open(self.save, 'r')
        self.Lines = self.file.readlines()
        self.text = []
        for line in self.Lines:
            temp = line.strip()
            if temp != '':
                self.text.append(int(temp))
        self.file.close()

    def write_score(self, number):
        self.text.append(number)
        self.text.sort(reverse=True)
        self.file = open(self.save, 'w')
        if len(self.text) <= 10:
            for i in range(len(self.text)):
                self.file.write(str(self.text[i]) + "\n")
        else:
            for i in range(10):
                self.file.write(str(self.text[i]) + "\n")
        self.file.close()

    def reset_score(self):
        self.file = open(self.save, 'w')
        for i in range(10):
            self.file.write(str(0) + "\n")
        self.file.close()


class game_map:
    def __init__(self):
        self.map_text = []

    def einlesen(self, text_datei):
        self.map_text = []
        text_file = open(text_datei, "r", encoding="utf-8")
        lines = text_file.readlines()

        for i in lines:
            temp = []
            i.split()
            if "\n" in i:
                i = i[0:len(i) - 1]
            for j in range(len(i)):
                temp.append(i[j])

            self.map_text.append(temp)

        text_file.close()

    def change_tile(self, y, x, change):
        self.map_text[y][x] = change

    def point_map_check(self):
        temp = True
        for i in range(len(self.map_text)):
            if "•" in self.map_text[i]:
                temp = False
            elif "@" in self.map_text[i]:
                temp = False

        return temp


class player:
    def __init__(self):
        self.player_x = 16
        self.player_y = 24
        self.player_pic = None
        self.point = 0
        self.power_mode = False
        self.power_time_max = 64 * 2
        self.power_time = 0
        self.imun = 16 * 2
        self.max_imun = self.imun
        self.hit = False
        self.life = 3

    def check_wall(self, x, y, map_tiles):
        wall = False
        wall_sym = {0: "│", 1: "┌", 2: "┐", 3: "┌", 4: "┘", 5: "└", 6: "─"}
        new_x = self.player_x + x
        new_y = self.player_y + y

        for key in wall_sym:
            if wall_sym[key] == map_tiles.map_text[new_y][new_x]:
                wall = True

        return wall

    def check_teleport(self, map_tiles):
        if self.player_x == 0:
            self.player_x = len(map_tiles.map_text[0]) - 2
        elif self.player_y == 0:
            self.player_y = len(map_tiles.map_text[0]) - 2

        elif self.player_x == len(map_tiles.map_text[0]) - 1:
            self.player_x = 1
        elif self.player_y == len(map_tiles.map_text[0]) - 1:
            self.player_y = 1

        return self.player_x, self.player_y

    def points(self, map_tiles):
        if map_tiles.map_text[self.player_y][self.player_x] == "•":
            self.point += 10
        elif map_tiles.map_text[self.player_y][self.player_x] == "@":
            self.point += 100

    def check_hit(self, geister):
        for k in geister.ghosts:
            if (geister.ghosts[k][1] == self.player_x) and (geister.ghosts[k][0] == self.player_y) and \
                    not geister.ghost_imun[k]:
                self.hit = True
                if self.power_mode:
                    geister.ghost_hit[k] = True
                    self.point += 500
                break
            else:
                self.hit = False

    def player_move(self, x, y, map_tiles, geister):
        if not self.check_wall(x, y, map_tiles):
            map_tiles.change_tile(self.player_y, self.player_x, " ")
            self.player_x += x
            self.player_y += y
            if map_tiles.map_text[self.player_y][self.player_x] == "@":
                self.power_mode = True
                self.power_time += self.power_time_max
            self.check_teleport(map_tiles)
            self.points(map_tiles)
            map_tiles.change_tile(self.player_y, self.player_x, "G")

        if self.imun == self.max_imun:
            self.check_hit(geister)
            if self.hit:
                if not self.power_mode:
                    self.imun -= 1
                    self.life -= 1
                    self.hit = False

        else:
            self.imun -= 1
            if self.imun == 0:
                self.imun = self.max_imun

        if self.power_mode:
            self.power_time -= 1
            if self.power_time == 0:
                self.power_mode = False
                self.power_time = self.power_time_max


class ghost:
    def __init__(self):
        self.ghosts = {"ghost_blue": [16, 18], "ghost_orange": [16, 16],
                       "ghost_red": [14, 16], "ghost_purple": [16, 14]}
        self.random_moves = {"up": [0, -1], "down": [0, 1], "left": [1, -1], "right": [1, 1]}
        self.ghost_current = {"ghost_blue": None, "ghost_orange": None, "ghost_red": None, "ghost_purple": None}
        self.move = None
        self.left = False
        self.right = False
        self.down = False
        self.up = False
        self.possible_move = []
        self.first_moves = True
        self.ghost_hit = {"ghost_blue": False, "ghost_orange": False, "ghost_red": False, "ghost_purple": False}
        self.ghost_imun = {"ghost_blue": False, "ghost_orange": False, "ghost_red": False, "ghost_purple": False}
        self.ghosts_imun_max = 16 * 2
        self.ghost_imun_count = {"ghost_blue": self.ghosts_imun_max, "ghost_orange": self.ghosts_imun_max,
                                 "ghost_red": self.ghosts_imun_max, "ghost_purple": self.ghosts_imun_max}

    def move_check(self, geist, map_tiles):
        wall_sym = {0: "│", 1: "┌", 2: "┐", 3: "┌", 4: "┘", 5: "└", 6: "─"}
        new_x = geist[1]
        new_y = geist[0]

        left = 0
        right = 0
        up = 0
        down = 0

        self.possible_move = []

        for key in wall_sym:
            if wall_sym[key] != map_tiles.map_text[new_y][new_x - 1]:
                left += 1
            if wall_sym[key] != map_tiles.map_text[new_y][new_x + 1]:
                right += 1
            if wall_sym[key] != map_tiles.map_text[new_y - 1][new_x]:
                up += 1
            if wall_sym[key] != map_tiles.map_text[new_y + 1][new_x]:
                down += 1

        if left == 7:
            self.left = True
            self.possible_move.append("left")
        else:
            self.left = False
        if right == 7:
            self.right = True
            self.possible_move.append("right")
        else:
            self.right = False
        if up == 7:
            self.up = True
            self.possible_move.append("up")
        else:
            self.up = False
        if down == 7:
            self.down = True
            self.possible_move.append("down")
        else:
            self.down = False

    def move_ghost(self, map_tiles):

        for key in self.ghosts:

            if self.ghost_hit[key]:
                self.ghost_imun[key] = True
                self.ghost_hit[key] = False

            if self.ghost_imun[key]:
                self.ghost_imun_count[key] -= 1
                if self.ghost_imun_count[key] == 0:
                    self.ghost_imun_count[key] = self.ghosts_imun_max
                    self.ghost_imun[key] = False

            self.move_check(self.ghosts[key], map_tiles)

            if self.ghost_current[key] is None:
                self.ghost_current[key] = "up"
            elif (self.ghost_current[key] == "left") and (
                    (not self.left) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.possible_move[random.randint(0, len(self.possible_move) - 1)]

            elif (self.ghost_current[key] == "right") and (
                    (not self.right) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.possible_move[random.randint(0, len(self.possible_move) - 1)]

            elif (self.ghost_current[key] == "up") and (
                    (not self.up) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.possible_move[random.randint(0, len(self.possible_move) - 1)]

            elif (self.ghost_current[key] == "down") and (
                    (not self.down) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.possible_move[random.randint(0, len(self.possible_move) - 1)]

            self.ghosts[key][self.random_moves[self.ghost_current[key]][0]] += \
                self.random_moves[self.ghost_current[key]][1]

            if self.ghosts[key][0] == 0:
                self.ghosts[key][0] = len(map_tiles.map_text[0]) - 2

            if self.ghosts[key][1] == 0:
                self.ghosts[key][1] = len(map_tiles.map_text[0]) - 2

            if self.ghosts[key][0] == len(map_tiles.map_text[0]) - 1:
                self.ghosts[key][0] = 1

            if self.ghosts[key][1] == len(map_tiles.map_text[0]) - 1:
                self.ghosts[key][1] = 1

            if (self.ghosts[key][1] == 16) and (self.ghosts[key][0] == 14 or self.ghosts[key][0] == 15 or
                                                self.ghosts[key][0] == 16 or self.ghosts[key][0] == 17 or
                                                self.ghosts[key][0] == 18):
                self.ghost_current[key] = "up"


class pacman(QWidget):
    def __init__(self, hoehe, breite, map_read, directory_score):
        super().__init__()

        self.setWindowIcon(QIcon("logic/images/icon.png"))
        # Setzen des Icons
        my_app_id = 'by_Müller_Willi.MyPacman.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

        self.setWindowTitle('Pacman_Python')

        self.map_read = map_read
        self.directory_score = directory_score

        self.hoehe = hoehe
        self.breite = breite

        self.hoehe_half = self.hoehe // 2
        self.breite_half = self.breite // 2
        self.resize(self.breite, self.hoehe)
        self.setMinimumSize(self.breite, self.hoehe)

        # pygame.mixer.init()
        # pygame.mixer.music.load("logic/music/")
        # pygame.mixer.music.play(-1)
        # pygame.mixer.music.set_volume(0.02)

        self.lvl = 1

        self.tile_size = int(self.hoehe * (5 / 216))

        self.right = False
        self.down = False
        self.up = False
        self.left = False
        self.ani = False

        self.full = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animation)
        self.speed = 80
        self.timer.start(self.speed)

        self.show_gameover = False
        self.show_gameover_count = 0

        self.lvl_complete = False
        self.hit_switch = False

        self.links_oben = QImage("logic/images/links_oben.png")
        self.rechts_oben = QImage("logic/images/rechts_oben.png")
        self.links_unten = QImage("logic/images/links_unten.png")
        self.rechts_unten = QImage("logic/images/rechts_unten.png")
        self.horizontal = QImage("logic/images/horizontal.png")
        self.vertikal = QImage("logic/images/vertikal.png")
        self.point = QImage("logic/images/point.png")
        self.power_up = QImage("logic/images/power_up.png")
        self.arcade = QImage("logic/images/arcade.png")
        self.herz = QImage("logic/images/herz.png")

        self.spieler_img = [QImage("logic/images/player_idle.png"), QImage("logic/images/player_left.png"),
                            QImage("logic/images/player_right.png"), QImage("logic/images/player_up.png"),
                            QImage("logic/images/player_down.png"),
                            QImage("logic/images/player_idle_hit.png"),
                            QImage("logic/images/player_left_hit.png"), QImage("logic/images/player_right_hit.png"),
                            QImage("logic/images/player_up_hit.png"), QImage("logic/images/player_down_hit.png"),
                            QImage("logic/images/player_idle_hit2.png"),
                            QImage("logic/images/player_left_hit2.png"), QImage("logic/images/player_right_hit2.png"),
                            QImage("logic/images/player_up_hit2.png"), QImage("logic/images/player_down_hit2.png")
                            ]

        self.blue_ghost_img = ["logic/images/geist_blau.png"]
        self.orange_ghost_img = ["logic/images/geist_orange.png"]
        self.red_ghost_img = ["logic/images/geist_rot.png"]
        self.purple_ghost_img = ["logic/images/geist_lila.png"]

        # geister
        self.geister = ghost()

        self.geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
        self.geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
        self.geister.ghosts["ghost_red"].extend(self.red_ghost_img)
        self.geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)

        self.spieler_index = 0
        self.spieler_punkte = 0

        self.verschiebung_x = int(self.breite * (5 / 48))
        self.verschiebung_y = int(self.hoehe * (5 / 36))

        # Map einlesen
        self.map_tiles = game_map()
        self.map_tiles.einlesen(self.map_read)

        # Highscore
        self.score = highscore(self.directory_score)

        # spieler
        self.spieler = player()

    def animation(self):
        if self.spieler.life > 0:
            if self.ani:
                self.spieler_index = 0
                if self.spieler.imun < self.spieler.max_imun:
                    if self.spieler.imun % 4 == 0:
                        self.hit_switch = True
                    elif self.spieler.imun % 2 == 0:
                        self.hit_switch = False

                    if not self.hit_switch:
                        self.spieler_index = 5
                    else:
                        self.spieler_index = 10

                self.ani = False

            else:
                if self.left:
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)
                    self.spieler_index = 1
                    if self.spieler.imun < self.spieler.max_imun:
                        if self.spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif self.spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 6
                        else:
                            self.spieler_index = 11

                    self.spieler.player_move(-1, 0, self.map_tiles, self.geister)
                    self.geister.move_ghost(self.map_tiles)
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)

                    self.ani = True

                if self.right:
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)
                    self.spieler_index = 2
                    if self.spieler.imun < self.spieler.max_imun:
                        if self.spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif self.spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 7
                        else:
                            self.spieler_index = 12

                    self.spieler.player_move(1, 0, self.map_tiles, self.geister)
                    self.geister.move_ghost(self.map_tiles)
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)

                    self.ani = True

                if self.up:
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)
                    self.spieler_index = 3
                    if self.spieler.imun < self.spieler.max_imun:
                        if self.spieler.imun % 4 == 0:
                            self.hit_switch = True
                        elif self.spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 8
                        else:
                            self.spieler_index = 13

                    self.spieler.player_move(0, -1, self.map_tiles, self.geister)
                    self.geister.move_ghost(self.map_tiles)

                    self.ani = True

                if self.down:
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)
                    self.spieler_index = 4
                    if self.spieler.imun < self.spieler.max_imun:
                        if self.spieler.imun % 3 == 0:
                            self.hit_switch = True
                        elif self.spieler.imun % 2 == 0:
                            self.hit_switch = False

                        if not self.hit_switch:
                            self.spieler_index = 9
                        else:
                            self.spieler_index = 14

                    self.spieler.player_move(0, 1, self.map_tiles, self.geister)
                    self.geister.move_ghost(self.map_tiles)
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)

                    self.ani = True

            self.spieler_punkte = self.spieler.point
            self.lvl_complete = self.map_tiles.point_map_check()

            if self.lvl_complete:
                self.geister.ghosts = {"ghost_blue": [16, 18], "ghost_orange": [16, 16],
                                       "ghost_red": [14, 16], "ghost_purple": [16, 14]}

                self.geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
                self.geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
                self.geister.ghosts["ghost_red"].extend(self.red_ghost_img)
                self.geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)

                self.lvl_complete = False
                self.lvl += 1
                self.spieler.player_x = 16
                self.spieler.player_y = 24
                # ändern
                self.map_tiles.einlesen(self.map_read)
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

        painter.drawText(int(self.breite * (7 / 12)), int(self.hoehe * (23 / 108)), "Level: " + str(self.lvl))

        if self.spieler.power_mode:
            painter.drawText(int(self.breite * (71 / 96)), int(self.hoehe * (23 / 108)),
                             "Power: " + str(self.spieler.power_time))

        painter.setFont(QFont("times", 10))

        painter.drawText(int(self.hoehe * (5 / 54)), int(self.hoehe * (103 / 108)), "Game made by Willi Müller")

        painter.setFont(QFont("times", 29))

        painter.drawText(int(self.breite * (7 / 12)), int(self.hoehe * (91 / 216)),
                         "Score: " + str(self.spieler_punkte))

        painter.drawText(int(self.breite * (7 / 12)), int(self.hoehe * (23 / 72)), "Life: ")

        painter.drawText(int(self.breite * (71 / 96)), int(self.hoehe * (53 / 108)), "Highscore")

        painter.setFont(QFont("times", 24))
        for i in range(min(10, len(self.score.text))):
            # Highscore malen lassen
            painter.drawText(int(self.breite * (7 / 12)),
                             int(self.hoehe * (29 / 54)) + (int(self.hoehe * (5 / 108)) * i),
                             str(i + 1) + ". ")
            painter.drawText(int(self.breite * (61 / 96)),
                             int(self.hoehe * (29 / 54)) + (int(self.hoehe * (5 / 108)) * i),
                             str(self.score.text[i]))

        if self.spieler.life == 0 and self.show_gameover:
            painter.setFont(QFont("times", 60))
            painter.drawText(int(self.breite * (71 / 96)), int(self.hoehe * (1 / 4)), "GAME OVER")
            painter.setFont(QFont("times", 35))
            painter.drawText(int(self.breite * (145 / 192)), int(self.hoehe * (1 / 3)), "Press R to Restart")

        for i in range(self.spieler.life):
            painter.drawImage(QRect(int(self.breite * (61 / 96)) + (int(self.breite * (5 / 96)) * i),
                                    int(self.hoehe * (29 / 108)), int(self.breite * (1 / 24)),
                                    int(self.hoehe * (2 / 27))), self.herz)

        pen.setColor(Qt.black)
        painter.setPen(pen)

        if self.spieler.life > 0:
            painter.drawImage(
                QRect((self.spieler.player_x * self.tile_size) + self.verschiebung_x,
                      (self.spieler.player_y * self.tile_size)
                      + self.verschiebung_y, self.tile_size, self.tile_size),
                self.spieler_img[self.spieler_index])

        painter.drawImage(QRect(self.verschiebung_x, 0, int(self.breite * (17 / 27)), self.verschiebung_y), self.arcade)

        for i in range(len(self.map_tiles.map_text)):
            for j in range(len(self.map_tiles.map_text[i])):
                if self.map_tiles.map_text[i][j] == "┌":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.links_oben)
                elif self.map_tiles.map_text[i][j] == "┐":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.rechts_oben)
                elif self.map_tiles.map_text[i][j] == "└":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.links_unten)
                elif self.map_tiles.map_text[i][j] == "┘":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.rechts_unten)
                elif self.map_tiles.map_text[i][j] == "─":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.horizontal)
                elif self.map_tiles.map_text[i][j] == "│":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.vertikal)
                elif self.map_tiles.map_text[i][j] == "@":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.power_up)
                elif self.map_tiles.map_text[i][j] == "•" or self.map_tiles.map_text[i][j] == "x":
                    painter.drawImage(QRect((j * self.tile_size) + self.verschiebung_x, (i * self.tile_size) +
                                            self.verschiebung_y, self.tile_size, self.tile_size), self.point)
                elif self.map_tiles.map_text[i][j] == " ":
                    pass

        for k in self.geister.ghosts:
            if self.spieler.power_mode and self.geister.ghost_imun[k]:
                painter.drawImage(QRect((self.geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x,
                                        (self.geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage("logic/images/geist_imun"))

            elif self.spieler.power_mode:
                painter.drawImage(QRect((self.geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x,
                                        (self.geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage("logic/images/geist_power"))

            else:
                painter.drawImage(QRect((self.geister.ghosts[k][1] * self.tile_size) + self.verschiebung_x,
                                        (self.geister.ghosts[k][0] * self.tile_size) + self.verschiebung_y,
                                        self.tile_size, self.tile_size), QImage(self.geister.ghosts[k][2]))

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
        if key == Qt.Key_F11:
            if not self.full:
                self.showFullScreen()
                self.full = True
            else:
                self.showNormal()
                self.full = False

        if key == Qt.Key_Escape:
            self.score.write_score(self.spieler.point)
            sys.exit()

        if (self.spieler.life == 0) and key == Qt.Key_R:
            self.geister.ghosts = {"ghost_blue": [16, 18], "ghost_orange": [16, 16],
                                   "ghost_red": [14, 16], "ghost_purple": [16, 14]}

            self.geister.ghosts["ghost_blue"].extend(self.blue_ghost_img)
            self.geister.ghosts["ghost_orange"].extend(self.orange_ghost_img)
            self.geister.ghosts["ghost_red"].extend(self.red_ghost_img)
            self.geister.ghosts["ghost_purple"].extend(self.purple_ghost_img)
            self.spieler.imun = self.spieler.max_imun
            self.spieler.player_x = 16
            self.spieler.player_y = 24
            self.score.write_score(self.spieler.point)
            self.spieler.point = 0
            self.lvl = 1
            self.spieler.life = 3
            # ändern
            self.map_tiles.einlesen(self.map_read)
            self.right = False
            self.down = False
            self.up = False
            self.left = False
