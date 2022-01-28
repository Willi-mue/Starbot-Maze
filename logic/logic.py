from io import open
import random


class highscore:

    def __init__(self):
        self.save = "highscore.txt"
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
        self.power_time_max = 64*2
        self.power_time = 0
        self.imun = 16*2
        self.max_imun = self.imun
        self.hit = False
        self.life = 3

    def check_wall(self, x, y):
        wall = False
        wall_sym = {0: "│", 1: "┌", 2: "┐", 3: "┌", 4: "┘", 5: "└", 6: "─"}
        new_x = self.player_x + x
        new_y = self.player_y + y

        for key in wall_sym:
            if wall_sym[key] == map_tiles.map_text[new_y][new_x]:
                wall = True

        return wall

    def check_teleport(self):
        if self.player_x == 0:
            self.player_x = len(map_tiles.map_text[0]) - 2
        elif self.player_y == 0:
            self.player_y = len(map_tiles.map_text[0]) - 2

        elif self.player_x == len(map_tiles.map_text[0]) - 1:
            self.player_x = 1
        elif self.player_y == len(map_tiles.map_text[0]) - 1:
            self.player_y = 1

        return self.player_x, self.player_y

    def points(self):
        if map_tiles.map_text[self.player_y][self.player_x] == "•":
            self.point += 10
        elif map_tiles.map_text[self.player_y][self.player_x] == "@":
            self.point += 100

    def check_hit(self):
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

    def player_move(self, x, y):
        if not self.check_wall(x, y):
            map_tiles.change_tile(self.player_y, self.player_x, " ")
            self.player_x += x
            self.player_y += y
            if map_tiles.map_text[self.player_y][self.player_x] == "@":
                self.power_mode = True
                self.power_time += self.power_time_max
            self.check_teleport()
            self.points()
            map_tiles.change_tile(self.player_y, self.player_x, "G")

        if self.imun == self.max_imun:
            self.check_hit()
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
        self.ghosts_imun_max = 16*2
        self.ghost_imun_count = {"ghost_blue": self.ghosts_imun_max, "ghost_orange": self.ghosts_imun_max,
                                 "ghost_red": self.ghosts_imun_max, "ghost_purple": self.ghosts_imun_max}

    def move_check(self, geist):
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

    def move_ghost(self):

        for key in self.ghosts:

            if self.ghost_hit[key]:
                self.ghost_imun[key] = True
                self.ghost_hit[key] = False

            if self.ghost_imun[key]:
                self.ghost_imun_count[key] -= 1
                if self.ghost_imun_count[key] == 0:
                    self.ghost_imun_count[key] = self.ghosts_imun_max
                    self.ghost_imun[key] = False

            self.move_check(self.ghosts[key])

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


# Map einlesen
map_tiles = game_map()
map_tiles.einlesen("../game/map.txt")
# Spieler erstellen
spieler = player()
# Geister erstellen
geister = ghost()
# Highscore
score = highscore()


