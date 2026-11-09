import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent, QSoundEffect
import ctypes
import json

from io import open
import random
import os

# Projektordner, damit das Spiel aus jedem Arbeitsverzeichnis heraus startet
BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pfad(*teile):
    return os.path.join(BASIS, *teile)


def setze_app_id():
    """Eigenes Taskleisten-Icon unter Windows; auf anderen Systemen nicht nötig."""
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('by_Müller_Willi.StarbotMaze.1.0')


def lade_bild(name, breite, hoehe=None):
    """Lädt logic/images/<name>.svg passend gerendert, sonst die PNG-Version."""
    hoehe = hoehe or breite
    svg = pfad("logic", "images", f"{name}.svg")
    if os.path.exists(svg):
        bild = QImage(breite, hoehe, QImage.Format_ARGB32_Premultiplied)
        bild.fill(Qt.transparent)
        painter = QPainter(bild)
        painter.setRenderHint(QPainter.Antialiasing)
        QSvgRenderer(svg).render(painter)
        painter.end()
        return bild
    return QImage(pfad("logic", "images", f"{name}.png"))


# Lautstärken für Musik und Effekte (Dateien kommen später, siehe DEV_TODO)
MUSIK_LAUTSTAERKE = 15      # 0 bis 100
EFFEKT_LAUTSTAERKE = 0.5    # 0.0 bis 1.0
EFFEKTE = ("stern", "kristall", "alien", "treffer", "gameover", "level")
SPIELSTAND = pfad("logic", "savegame.json")


class Audio:
    """Musik aus logic/music/ (Schleife) und Effekte aus logic/sounds/<name>.wav.
    Fehlende Dateien werden still übersprungen."""

    def __init__(self, parent):
        self.musik = None
        ordner = pfad("logic", "music")
        dateien = sorted(f for f in os.listdir(ordner)
                         if f.lower().endswith((".mp3", ".wav", ".ogg", ".m4a"))) if os.path.isdir(ordner) else []
        if dateien:
            self.playlist = QMediaPlaylist(parent)
            for f in dateien:
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(ordner, f))))
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.musik = QMediaPlayer(parent)
            self.musik.setPlaylist(self.playlist)
            self.musik.setVolume(MUSIK_LAUTSTAERKE)

        self.effekte = {}
        for name in EFFEKTE:
            datei = pfad("logic", "sounds", f"{name}.wav")
            if os.path.exists(datei):
                effekt = QSoundEffect(parent)
                effekt.setSource(QUrl.fromLocalFile(datei))
                effekt.setVolume(EFFEKT_LAUTSTAERKE)
                self.effekte[name] = effekt

    def musik_start(self):
        if self.musik:
            self.musik.play()

    def effekt(self, name):
        if name in self.effekte:
            self.effekte[name].play()


HINTERGRUND = QColor("#05070f")
NEON = QColor("#4cf0ff")
WEISS_TEXT = QColor("#f2f6ff")


def zeichne_sterne(painter, breite, hoehe, dichte=1 / 900, seed=7):
    """Fester Sternenhimmel: gleicher Seed ergibt immer dieselben Sterne."""
    rnd = random.Random(seed)
    painter.setPen(Qt.NoPen)
    for _ in range(int(breite * hoehe * dichte)):
        farbe = QColor(255, 255, 255, rnd.randint(70, 220))
        r = rnd.choice((0.6, 0.9, 1.3))
        painter.setBrush(farbe)
        painter.drawEllipse(QPointF(rnd.uniform(0, breite), rnd.uniform(0, hoehe)), r, r)


def erzeuge_banner(breite, hoehe):
    """Titel-Banner „STARBOT MAZE“ mit Sternen und Deko-Figuren, passend zur Größe gerendert."""
    bild = QImage(breite, hoehe, QImage.Format_ARGB32_Premultiplied)
    bild.fill(Qt.transparent)
    p = QPainter(bild)
    p.setRenderHint(QPainter.Antialiasing)

    zeichne_sterne(p, breite, hoehe, dichte=1 / 700)

    # Deko an den Rändern (x, y relativ, Größe relativ zur Höhe)
    deko = [("alien_gruen", 0.03, 0.12, 0.34), ("point", 0.11, 0.62, 0.22), ("alien_lila", 0.14, 0.18, 0.28),
            ("power_up", 0.05, 0.58, 0.3), ("player_right", 0.80, 0.14, 0.34), ("point", 0.87, 0.66, 0.2),
            ("alien_pink", 0.93, 0.2, 0.3), ("alien_gelb", 0.84, 0.56, 0.3)]
    for name, rx, ry, rs in deko:
        s = max(8, int(hoehe * rs))
        p.drawImage(int(breite * rx), int(hoehe * ry), lade_bild(name, s))

    font = QFont("Arial Black")
    font.setWeight(QFont.Black)
    font.setPixelSize(max(8, int(hoehe * 0.6)))
    font.setLetterSpacing(QFont.PercentageSpacing, 108)
    pfad = QPainterPath()
    pfad.addText(0, 0, font, "STARBOT MAZE")
    r = pfad.boundingRect()
    faktor = min(1.0, breite * 0.6 / r.width())
    p.translate(breite / 2, hoehe / 2)
    p.scale(faktor, faktor)
    p.translate(-r.center())

    # Neon-Schein, dann Verlauf, dann feine Kontur
    for breite_schein, alpha in ((hoehe * 0.14, 40), (hoehe * 0.07, 80)):
        p.strokePath(pfad, QPen(QColor(76, 240, 255, alpha), breite_schein, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    verlauf = QLinearGradient(0, r.top(), 0, r.bottom())
    verlauf.setColorAt(0, QColor("#f2feff"))
    verlauf.setColorAt(0.5, QColor("#4cf0ff"))
    verlauf.setColorAt(1, QColor("#b032ff"))
    p.fillPath(pfad, verlauf)
    p.strokePath(pfad, QPen(QColor(255, 255, 255, 200), max(1.0, hoehe * 0.012)))
    p.end()
    return bild


class highscore:

    def __init__(self, dir_highscore):
        self.save = dir_highscore
        self.text = []
        if not os.path.exists(self.save):
            open(self.save, 'w').close()
        with open(self.save, 'r') as datei:
            for line in datei:
                temp = line.strip()
                if temp.isdigit():
                    self.text.append(int(temp))
        self.text.sort(reverse=True)

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
    STERN = ("•", "x")  # x: Stern, der zugleich Kreuzung für die Aliens ist
    KRISTALL = "@"

    def __init__(self):
        self.map_text = []
        self.sterne = set()
        self.kristalle = set()

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

        self.sterne = {(y, x) for y, zeile in enumerate(self.map_text)
                       for x, zeichen in enumerate(zeile) if zeichen in self.STERN}
        self.kristalle = {(y, x) for y, zeile in enumerate(self.map_text)
                          for x, zeichen in enumerate(zeile) if zeichen == self.KRISTALL}

    def einsammeln(self, y, x):
        """Entfernt ein Sammelobjekt an (y, x) und sagt, was es war."""
        if (y, x) in self.sterne:
            self.sterne.discard((y, x))
            return "stern"
        if (y, x) in self.kristalle:
            self.kristalle.discard((y, x))
            return "kristall"
        return None

    def point_map_check(self):
        return not self.sterne and not self.kristalle


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
        art = map_tiles.einsammeln(self.player_y, self.player_x)
        if art == "stern":
            self.point += 10
        elif art == "kristall":
            self.point += 100
            self.power_mode = True
            self.power_time += self.power_time_max

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
            self.player_x += x
            self.player_y += y
            self.check_teleport(map_tiles)
            self.points(map_tiles)

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


class aliens:
    # Wie oft ein Alien an einer Kreuzung den kürzesten Weg zum Spieler nimmt (0 = zufällig, 1 = immer).
    JAGD = {"alien_pink": 0.9, "alien_lila": 0.75, "alien_gruen": 0.6, "alien_gelb": 0.45}
    JAGD_PRO_LEVEL = 0.05
    JAGD_MAX = 0.95
    WAENDE = set("│┌┐┘└─")
    GEGENRICHTUNG = {"left": "right", "right": "left", "up": "down", "down": "up"}

    def __init__(self):
        self.ghosts = {"alien_gruen": [16, 18], "alien_gelb": [16, 16],
                       "alien_pink": [14, 16], "alien_lila": [16, 14]}
        self.random_moves = {"up": [0, -1], "down": [0, 1], "left": [1, -1], "right": [1, 1]}
        self.ghost_current = {"alien_gruen": None, "alien_gelb": None, "alien_pink": None, "alien_lila": None}
        self.move = None
        self.left = False
        self.right = False
        self.down = False
        self.up = False
        self.possible_move = []
        self.first_moves = True
        self.ghost_hit = {"alien_gruen": False, "alien_gelb": False, "alien_pink": False, "alien_lila": False}
        self.ghost_imun = {"alien_gruen": False, "alien_gelb": False, "alien_pink": False, "alien_lila": False}
        self.ghosts_imun_max = 16 * 2
        self.ghost_imun_count = {"alien_gruen": self.ghosts_imun_max, "alien_gelb": self.ghosts_imun_max,
                                 "alien_pink": self.ghosts_imun_max, "alien_lila": self.ghosts_imun_max}

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

    def entfernungen(self, map_tiles, start):
        """Breitensuche: Schritte von start (y, x) zu jedem erreichbaren Feld."""
        dist = {start: 0}
        schlange = [start]
        for y, x in schlange:
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if (ny, nx) in dist or not (0 <= ny < len(map_tiles.map_text)):
                    continue
                zeile = map_tiles.map_text[ny]
                if 0 <= nx < len(zeile) and zeile[nx] not in self.WAENDE:
                    dist[(ny, nx)] = dist[(y, x)] + 1
                    schlange.append((ny, nx))
        return dist

    def nachbar(self, geist, richtung):
        pos = [geist[0], geist[1]]
        achse, schritt = self.random_moves[richtung]
        pos[achse] += schritt
        return pos[0], pos[1]

    def richtung_waehlen(self, key, dist, flucht, level):
        moeglich = list(self.possible_move)
        # Nicht grundlos umdrehen, solange es eine andere Richtung gibt
        gegen = self.GEGENRICHTUNG.get(self.ghost_current[key])
        if len(moeglich) > 1 and gegen in moeglich:
            moeglich.remove(gegen)

        jagd = min(self.JAGD_MAX, self.JAGD.get(key, 0.3) + self.JAGD_PRO_LEVEL * (level - 1))
        if dist is not None and not self.ghost_imun[key] and random.random() < jagd:
            def abstand(richtung):
                return dist.get(self.nachbar(self.ghosts[key], richtung), 10 ** 6)
            return max(moeglich, key=abstand) if flucht else min(moeglich, key=abstand)
        return random.choice(moeglich)

    def move_ghost(self, map_tiles, spieler=None, flucht=False, level=1):
        dist = self.entfernungen(map_tiles, spieler) if spieler else None

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

                self.ghost_current[key] = self.richtung_waehlen(key, dist, flucht, level)

            elif (self.ghost_current[key] == "right") and (
                    (not self.right) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.richtung_waehlen(key, dist, flucht, level)

            elif (self.ghost_current[key] == "up") and (
                    (not self.up) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.richtung_waehlen(key, dist, flucht, level)

            elif (self.ghost_current[key] == "down") and (
                    (not self.down) or (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "x") or
                    (map_tiles.map_text[self.ghosts[key][0]][self.ghosts[key][1]] == "X")):

                self.ghost_current[key] = self.richtung_waehlen(key, dist, flucht, level)

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


class spiel(QWidget):
    def __init__(self, hoehe, breite, map_read, directory_score):
        super().__init__()

        self.setWindowIcon(QIcon(pfad("logic", "images", "icon.svg")))
        setze_app_id()

        self.setWindowTitle('Starbot Maze')

        self.map_read = map_read
        self.directory_score = directory_score

        self.hoehe = hoehe
        self.breite = breite

        self.hoehe_half = self.hoehe // 2
        self.breite_half = self.breite // 2
        self.resize(self.breite, self.hoehe)
        self.setMinimumSize(self.breite, self.hoehe)

        self.audio = Audio(self)

        self.lvl = 1

        # Map einlesen (vor dem Layout, weil die Kachelgröße von der Map-Größe abhängt)
        self.map_tiles = game_map()
        self.map_tiles.einlesen(self.map_read)
        self.layout_berechnen()

        self.right = False
        self.down = False
        self.up = False
        self.left = False
        self.ani = False

        self.full = False
        self.score_saved = False

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.animation)
        self.speed = 80
        self.timer.start(self.speed)

        # Flüssige Darstellung: Logik springt kachelweise (alle 2 Takte), gezeichnet wird mit ~60 FPS
        # und die Figuren gleiten zwischen alter und neuer Kachel
        self.uhr = QElapsedTimer()
        self.uhr.start()
        self.bewegungs_dauer = 2 * self.speed
        self.render_alt = {}
        self.render_start = {}
        self.frame_timer = QTimer(self)
        self.frame_timer.setTimerType(Qt.PreciseTimer)
        self.frame_timer.timeout.connect(self.update)
        self.frame_timer.start(16)

        self.show_gameover = False
        self.show_gameover_count = 0

        self.lvl_complete = False
        self.hit_switch = False

        t = self.tile_size
        self.links_oben = lade_bild("links_oben", t)
        self.rechts_oben = lade_bild("rechts_oben", t)
        self.links_unten = lade_bild("links_unten", t)
        self.rechts_unten = lade_bild("rechts_unten", t)
        self.horizontal = lade_bild("horizontal", t)
        self.vertikal = lade_bild("vertikal", t)
        self.point = lade_bild("point", t)
        self.power_up = lade_bild("power_up", t)
        self.herz = lade_bild("herz", int(t * 1.3))
        self.geist_imun_img = lade_bild("alien_kern", t)
        self.geist_power_img = lade_bild("alien_eis", t)

        self.spieler_img = [lade_bild(f"player_{richtung}{farbe}", t)
                            for farbe in ("", "_hit", "_hit2")
                            for richtung in ("idle", "left", "right", "up", "down")]

        # Aliens merken sich nur ihren Bildnamen, die Bilder liegen fertig gerendert hier
        self.geister_bilder = {name: lade_bild(name, t)
                               for name in ("alien_gruen", "alien_gelb", "alien_pink", "alien_lila")}

        self.gruen_alien_img = ["alien_gruen"]
        self.gelb_alien_img = ["alien_gelb"]
        self.pink_alien_img = ["alien_pink"]
        self.lila_alien_img = ["alien_lila"]

        # geister
        self.geister = aliens()

        self.geister.ghosts["alien_gruen"].extend(self.gruen_alien_img)
        self.geister.ghosts["alien_gelb"].extend(self.gelb_alien_img)
        self.geister.ghosts["alien_pink"].extend(self.pink_alien_img)
        self.geister.ghosts["alien_lila"].extend(self.lila_alien_img)

        self.spieler_index = 0
        self.spieler_punkte = 0

        # Highscore
        self.score = highscore(self.directory_score)

        # spieler
        self.spieler = player()

        # Alles, was sich nie ändert, einmal vorzeichnen
        self.hintergrund = self.hintergrund_erzeugen()

    def positionen(self):
        pos = {"spieler": (self.spieler.player_x, self.spieler.player_y)}
        for k, g in self.geister.ghosts.items():
            pos[k] = (g[1], g[0])
        return pos

    def animation(self):
        vorher = self.positionen()
        punkte, leben, level = self.spieler.point, self.spieler.life, self.lvl
        self.logik_takt()
        jetzt = self.uhr.elapsed()
        for k, neu in self.positionen().items():
            alt = vorher.get(k, neu)
            if alt != neu:
                self.render_alt[k] = alt
                self.render_start[k] = jetzt
        self.ereignisse(self.spieler.point - punkte, leben, level)

    def ereignisse(self, punkte_neu, leben_vorher, level_vorher):
        if self.lvl > level_vorher:
            self.audio.effekt("level")
        elif punkte_neu >= 500:
            self.audio.effekt("alien")
        elif punkte_neu >= 100:
            self.audio.effekt("kristall")
        elif punkte_neu > 0:
            self.audio.effekt("stern")

        if self.spieler.life < leben_vorher:
            if self.spieler.life == 0:
                self.audio.effekt("gameover")
                self.spielstand_loeschen()
            else:
                self.audio.effekt("treffer")

    def showEvent(self, event):
        self.audio.musik_start()
        super().showEvent(event)

    # ---------- Spielstand ----------

    @staticmethod
    def spielstand_vorhanden():
        return os.path.exists(SPIELSTAND)

    @staticmethod
    def spielstand_loeschen():
        if os.path.exists(SPIELSTAND):
            os.remove(SPIELSTAND)

    def spielstand_speichern(self):
        daten = {
            "level": self.lvl,
            "punkte": self.spieler.point,
            "leben": self.spieler.life,
            "spieler": [self.spieler.player_x, self.spieler.player_y],
            "power_time": self.spieler.power_time if self.spieler.power_mode else 0,
            "sterne": sorted(self.map_tiles.sterne),
            "kristalle": sorted(self.map_tiles.kristalle),
            "aliens": {k: [g[0], g[1]] for k, g in self.geister.ghosts.items()},
        }
        with open(SPIELSTAND, "w", encoding="utf-8") as datei:
            json.dump(daten, datei)

    def spielstand_laden(self):
        """Stellt den gespeicherten Stand wieder her. Gibt False zurück, wenn das nicht klappt."""
        try:
            with open(SPIELSTAND, encoding="utf-8") as datei:
                daten = json.load(datei)
            self.lvl = int(daten["level"])
            self.spieler.point = self.spieler_punkte = int(daten["punkte"])
            self.spieler.life = int(daten["leben"])
            self.spieler.player_x, self.spieler.player_y = daten["spieler"]
            self.spieler.power_time = int(daten["power_time"]) or self.spieler.power_time_max
            self.spieler.power_mode = int(daten["power_time"]) > 0
            self.map_tiles.sterne = {tuple(p) for p in daten["sterne"]}
            self.map_tiles.kristalle = {tuple(p) for p in daten["kristalle"]}
            for k, (y, x) in daten["aliens"].items():
                self.geister.ghosts[k][0], self.geister.ghosts[k][1] = y, x
        except (OSError, ValueError, KeyError, TypeError):
            return False
        self.render_alt.clear()
        # Ein Spielstand gilt nur einmal: nach dem Laden weg, damit man nicht nach einem Fehler neu lädt
        self.spielstand_loeschen()
        return True

    def beenden(self):
        """Beim Verlassen: laufendes Spiel als Spielstand sichern, beendetes Spiel in die Highscores."""
        if self.score_saved:
            return
        self.score_saved = True
        if self.spieler.life > 0 and self.spieler.point > 0:
            self.spielstand_speichern()
        elif self.spieler.point > 0:
            self.score.write_score(self.spieler.point)

    def render_pos(self, key, x, y):
        """Zeichenposition in Kacheln, zwischen alter und neuer Kachel interpoliert."""
        if key not in self.render_alt:
            return x, y
        ax, ay = self.render_alt[key]
        if abs(ax - x) + abs(ay - y) != 1:  # Teleport, Neustart: nicht gleiten
            return x, y
        f = min(1.0, (self.uhr.elapsed() - self.render_start[key]) / self.bewegungs_dauer)
        return ax + (x - ax) * f, ay + (y - ay) * f

    def logik_takt(self):
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
                    self.geister.move_ghost(self.map_tiles, (self.spieler.player_y, self.spieler.player_x),
                                            self.spieler.power_mode, self.lvl)
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
                    self.geister.move_ghost(self.map_tiles, (self.spieler.player_y, self.spieler.player_x),
                                            self.spieler.power_mode, self.lvl)
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
                    self.geister.move_ghost(self.map_tiles, (self.spieler.player_y, self.spieler.player_x),
                                            self.spieler.power_mode, self.lvl)

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
                    self.geister.move_ghost(self.map_tiles, (self.spieler.player_y, self.spieler.player_x),
                                            self.spieler.power_mode, self.lvl)
                    self.spieler.player_move(0, 0, self.map_tiles, self.geister)

                    self.ani = True

            self.spieler_punkte = self.spieler.point
            self.lvl_complete = self.map_tiles.point_map_check()

            if self.lvl_complete:
                self.geister.ghosts = {"alien_gruen": [16, 18], "alien_gelb": [16, 16],
                                       "alien_pink": [14, 16], "alien_lila": [16, 14]}

                self.geister.ghosts["alien_gruen"].extend(self.gruen_alien_img)
                self.geister.ghosts["alien_gelb"].extend(self.gelb_alien_img)
                self.geister.ghosts["alien_pink"].extend(self.pink_alien_img)
                self.geister.ghosts["alien_lila"].extend(self.lila_alien_img)

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

    # ---------- Layout ----------

    def layout_berechnen(self):
        """Spielfeld + Infotafel werden gemeinsam zentriert, das Banner sitzt mittig darüber."""
        h = self.hoehe
        zeilen = len(self.map_tiles.map_text)
        spalten = max(len(z) for z in self.map_tiles.map_text)

        banner_hoehe = int(h * 0.12)
        rand = int(h * 0.03)
        feld_oben = banner_hoehe + rand
        self.tile_size = int((h - feld_oben - rand * 1.5) / zeilen)

        feld_breite = spalten * self.tile_size
        feld_hoehe = zeilen * self.tile_size
        tafel_breite = int(h * 0.40)
        abstand = int(h * 0.05)
        gesamt = feld_breite + abstand + tafel_breite
        links = (self.breite - gesamt) // 2

        self.verschiebung_x = links
        self.verschiebung_y = feld_oben
        self.feld_rect = QRect(links, feld_oben, feld_breite, feld_hoehe)
        self.tafel_rect = QRect(links + feld_breite + abstand, feld_oben, tafel_breite, feld_hoehe)
        self.banner_rect = QRect(links, int(h * 0.01), gesamt, banner_hoehe)

    def px(self, groesse):
        """Pixelgröße, ausgelegt für 1080p, skaliert auf die Spielhöhe."""
        return max(1, round(groesse * self.hoehe / 1080))

    def schrift(self, groesse, fett=True):
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setBold(fett)
        font.setPixelSize(self.px(groesse))
        return font

    def tafel_abschnitte(self):
        """Positionen der Abschnitte in der Infotafel (gemeinsam für Vorzeichnen und Werte)."""
        r = self.tafel_rect
        innen = self.px(28)
        y = r.top() + innen
        return {
            "x": r.left() + innen,
            "breite": r.width() - 2 * innen,
            "level_score": y,
            "leben": y + self.px(120),
            "power": y + self.px(230),
            "highscore": y + self.px(340),
            "hilfe": r.bottom() - innen - self.px(70),
        }

    def hintergrund_erzeugen(self):
        """Hintergrund, Sterne, Banner, Wände und feste Beschriftungen einmalig als Bild."""
        bild = QPixmap(self.breite, self.hoehe)
        bild.fill(HINTERGRUND)
        p = QPainter(bild)
        p.setRenderHint(QPainter.Antialiasing)
        zeichne_sterne(p, self.breite, self.hoehe, dichte=1 / 2500, seed=11)

        p.drawImage(self.banner_rect.topLeft(),
                    erzeuge_banner(self.banner_rect.width(), self.banner_rect.height()))

        # Spielfeld auf eigener, etwas hellerer Fläche (keine Hintergrundsterne zwischen den Sammel-Sternen)
        rund = self.px(14)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#060a17"))
        rand = self.px(8)
        p.drawRoundedRect(QRectF(self.feld_rect).adjusted(-rand, -rand, rand, rand), rund, rund)

        wand_bilder = {"┌": self.links_oben, "┐": self.rechts_oben, "└": self.links_unten,
                       "┘": self.rechts_unten, "─": self.horizontal, "│": self.vertikal}
        t = self.tile_size
        for i, zeile in enumerate(self.map_tiles.map_text):
            for j, zeichen in enumerate(zeile):
                if zeichen in wand_bilder:
                    p.drawImage(self.verschiebung_x + j * t, self.verschiebung_y + i * t, wand_bilder[zeichen])

        # Infotafel
        p.setBrush(QColor(12, 18, 36, 235))
        p.setPen(QPen(QColor(76, 240, 255, 140), self.px(2)))
        p.drawRoundedRect(QRectF(self.tafel_rect), rund, rund)

        a = self.tafel_abschnitte()
        p.setFont(self.schrift(18))
        p.setPen(QColor(140, 160, 190))
        p.drawText(a["x"], a["level_score"] + self.px(18), "LEVEL")
        p.drawText(a["x"] + a["breite"] // 2, a["level_score"] + self.px(18), "SCORE")
        p.drawText(a["x"], a["leben"] + self.px(18), "LIVES")
        p.drawText(a["x"], a["power"] + self.px(18), "POWER")
        p.drawText(a["x"], a["highscore"] + self.px(18), "HIGHSCORES")

        p.setPen(QPen(QColor(76, 240, 255, 60), self.px(1)))
        for key in ("leben", "power", "highscore", "hilfe"):
            y = a[key] - self.px(22)
            p.drawLine(a["x"], y, a["x"] + a["breite"], y)

        p.setFont(self.schrift(14, fett=False))
        p.setPen(QColor(110, 125, 150))
        p.drawText(a["x"], a["hilfe"] + self.px(14), "WASD / ARROWS   MOVE")
        p.drawText(a["x"], a["hilfe"] + self.px(36), "F11 FULLSCREEN  ESC QUIT")
        p.setPen(QColor(80, 92, 115))
        p.drawText(a["x"], a["hilfe"] + self.px(62), "Game made by Willi Müller")
        p.end()
        return bild

    # ---------- Zeichnen ----------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), HINTERGRUND)
        painter.translate((self.width() - self.breite) // 2, (self.height() - self.hoehe) // 2)
        painter.drawPixmap(0, 0, self.hintergrund)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        t = self.tile_size
        ox, oy = self.verschiebung_x, self.verschiebung_y

        # Sammelobjekte
        for i, j in self.map_tiles.sterne:
            painter.drawImage(ox + j * t, oy + i * t, self.point)
        for i, j in self.map_tiles.kristalle:
            painter.drawImage(ox + j * t, oy + i * t, self.power_up)

        # Aliens
        for k, g in self.geister.ghosts.items():
            if self.spieler.power_mode and self.geister.ghost_imun[k]:
                bild = self.geist_imun_img
            elif self.spieler.power_mode:
                bild = self.geist_power_img
            else:
                bild = self.geister_bilder[g[2]]
            x, y = self.render_pos(k, g[1], g[0])
            painter.drawImage(QPointF(ox + x * t, oy + y * t), bild)

        # Spieler
        if self.spieler.life > 0:
            x, y = self.render_pos("spieler", self.spieler.player_x, self.spieler.player_y)
            painter.drawImage(QPointF(ox + x * t, oy + y * t), self.spieler_img[self.spieler_index])

        self.tafel_zeichnen(painter)

        if self.spieler.life == 0:
            self.game_over_zeichnen(painter)

    def tafel_zeichnen(self, painter):
        a = self.tafel_abschnitte()
        painter.setPen(WEISS_TEXT)
        painter.setFont(self.schrift(40))
        painter.drawText(a["x"], a["level_score"] + self.px(68), str(self.lvl))
        painter.drawText(a["x"] + a["breite"] // 2, a["level_score"] + self.px(68), str(self.spieler_punkte))

        herz = self.herz.width()
        for i in range(self.spieler.life):
            painter.drawImage(a["x"] + i * (herz + self.px(10)), a["leben"] + self.px(32), self.herz)

        # Power-Balken
        balken = QRectF(a["x"], a["power"] + self.px(36), a["breite"], self.px(22))
        rund = balken.height() / 2
        painter.setPen(QPen(QColor(76, 240, 255, 90), self.px(1)))
        painter.setBrush(QColor(255, 255, 255, 12))
        painter.drawRoundedRect(balken, rund, rund)
        if self.spieler.power_mode:
            anteil = max(0.0, min(1.0, self.spieler.power_time / self.spieler.power_time_max))
            gefuellt = QRectF(balken.x(), balken.y(), balken.width() * anteil, balken.height())
            verlauf = QLinearGradient(balken.topLeft(), balken.topRight())
            verlauf.setColorAt(0, QColor("#b032ff"))
            verlauf.setColorAt(1, NEON)
            painter.setPen(Qt.NoPen)
            painter.setBrush(verlauf)
            painter.drawRoundedRect(gefuellt, rund, rund)

        # Highscores (Top 5)
        painter.setFont(self.schrift(24))
        zeile = self.px(40)
        for i, wert in enumerate(self.score.text[:5]):
            y = a["highscore"] + self.px(60) + i * zeile
            painter.setPen(QColor(140, 160, 190))
            painter.drawText(a["x"], y, f"{i + 1}.")
            painter.setPen(WEISS_TEXT)
            painter.drawText(QRect(a["x"], y - zeile + self.px(8), a["breite"], zeile),
                             Qt.AlignRight | Qt.AlignBottom, str(wert))

    def game_over_zeichnen(self, painter):
        r = QRectF(self.feld_rect)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(3, 5, 12, 200))
        painter.drawRoundedRect(r, self.px(14), self.px(14))

        painter.setPen(NEON)
        painter.setFont(self.schrift(84))
        painter.drawText(r.adjusted(0, 0, 0, -r.height() * 0.18), Qt.AlignCenter, "GAME OVER")
        painter.setPen(WEISS_TEXT)
        painter.setFont(self.schrift(30))
        painter.drawText(r, Qt.AlignCenter, f"SCORE  {self.spieler_punkte}")
        if self.show_gameover:
            painter.setFont(self.schrift(24))
            painter.setPen(QColor(200, 210, 230))
            painter.drawText(r.adjusted(0, r.height() * 0.16, 0, 0), Qt.AlignCenter, "PRESS R TO RESTART")

    def closeEvent(self, event):
        self.beenden()
        event.accept()

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
            self.beenden()
            sys.exit()

        if (self.spieler.life == 0) and key == Qt.Key_R:
            self.geister.ghosts = {"alien_gruen": [16, 18], "alien_gelb": [16, 16],
                                   "alien_pink": [14, 16], "alien_lila": [16, 14]}

            self.geister.ghosts["alien_gruen"].extend(self.gruen_alien_img)
            self.geister.ghosts["alien_gelb"].extend(self.gelb_alien_img)
            self.geister.ghosts["alien_pink"].extend(self.pink_alien_img)
            self.geister.ghosts["alien_lila"].extend(self.lila_alien_img)
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
