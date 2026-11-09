import math

from logic.logic import *

# Farben im Stil des Spiels (HINTERGRUND und NEON kommen aus logic.py)
WEISS = QColor("white")
GRAU = QColor(90, 100, 120)


class menu(QWidget):
    BREITE = 760
    HOEHE = 600

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Starbot Maze')
        self.setWindowIcon(QIcon(pfad("logic", "images", "icon.svg")))
        self.setFixedSize(self.BREITE, self.HOEHE)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.game_breite, self.game_hoehe = self.screen_resolution()
        self.game = spiel(self.game_hoehe, self.game_breite,
                          pfad("game", "map.txt"), pfad("logic", "highscore.txt"))

        # (Text, Aktion, aktiv)
        self.eintraege = [
            ("START", self.start_button, True),
            ("LOAD", self.load_button, spiel.spielstand_vorhanden()),
            ("EXIT", self.end_game, True),
        ]
        self.auswahl = 0
        self.eintrag_rects = []

        self.banner = erzeuge_banner(self.BREITE - 100, 84)
        self.spieler_img = lade_bild("player_right", 32)
        self.punkt_img = lade_bild("point", 32)
        self.geister_img = [lade_bild(name, 32) for name in ("alien_pink", "alien_lila", "alien_gruen", "alien_gelb")]
        self.cursor_img = lade_bild("player_right", 30)

        # Animation: Der Roboter sammelt Sterne ein, die Aliens jagen hinterher
        self.anim_x = -60.0
        self.anim_tick = 0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animieren)
        self.anim_timer.start(30)

    @staticmethod
    def screen_resolution():
        # Größtes 16:9-Format, das auf den Hauptbildschirm passt
        size = QApplication.primaryScreen().size()
        if size.width() * 9 <= size.height() * 16:
            return size.width(), size.width() * 9 // 16
        return size.height() * 16 // 9, size.height()

    # ---------- Aktionen ----------

    def start_button(self):
        self.anim_timer.stop()
        self.game.showFullScreen()
        self.game.full = True
        self.hide()

    def end_game(self):
        sys.exit()

    def load_button(self):
        if self.game.spielstand_laden():
            self.start_button()
        else:
            # Spielstand unlesbar: Eintrag deaktivieren, statt abzustürzen
            self.eintraege[1] = ("LOAD", self.load_button, False)
            self.auswahl = 0
            self.update()

    def ausfuehren(self):
        text, aktion, aktiv = self.eintraege[self.auswahl]
        if aktiv:
            aktion()

    def auswahl_bewegen(self, richtung):
        # Überspringt deaktivierte Einträge
        for _ in range(len(self.eintraege)):
            self.auswahl = (self.auswahl + richtung) % len(self.eintraege)
            if self.eintraege[self.auswahl][2]:
                break
        self.update()

    # ---------- Eingabe ----------

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_W, Qt.Key_Up):
            self.auswahl_bewegen(-1)
        elif key in (Qt.Key_S, Qt.Key_Down):
            self.auswahl_bewegen(1)
        elif key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.ausfuehren()
        elif key == Qt.Key_Escape:
            self.end_game()

    def eintrag_bei(self, pos):
        for i, rect in enumerate(self.eintrag_rects):
            if rect.contains(pos) and self.eintraege[i][2]:
                return i
        return None

    def mouseMoveEvent(self, event):
        i = self.eintrag_bei(event.pos())
        if i is not None and i != self.auswahl:
            self.auswahl = i
            self.update()
        self.setCursor(Qt.PointingHandCursor if i is not None else Qt.ArrowCursor)

    def mousePressEvent(self, event):
        i = self.eintrag_bei(event.pos())
        if event.button() == Qt.LeftButton and i is not None:
            self.auswahl = i
            self.ausfuehren()

    # ---------- Zeichnen ----------

    def animieren(self):
        self.anim_x += 3
        self.anim_tick += 1
        # Roboter plus 4 Aliens im Abstand von 44 px müssen ganz durchgelaufen sein
        if self.anim_x > self.BREITE + 5 * 44:
            self.anim_x = -60.0
        self.update()

    @staticmethod
    def schrift(groesse, fett=True):
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPixelSize(groesse)
        font.setBold(fett)
        font.setLetterSpacing(QFont.AbsoluteSpacing, groesse * 0.15)
        return font

    def rahmen_zeichnen(self, painter):
        # Doppelte Wand wie im Labyrinth
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(NEON, 3))
        painter.drawRoundedRect(QRectF(14, 14, self.BREITE - 28, self.HOEHE - 28), 14, 14)
        painter.drawRoundedRect(QRectF(26, 26, self.BREITE - 52, self.HOEHE - 52), 8, 8)

    def animation_zeichnen(self, painter, y):
        groesse = 32
        links = 60
        rechts = self.BREITE - 60

        # Tunnel wie im Spielfeld: zwei Wände, an den Enden offen
        painter.setPen(QPen(NEON, 3))
        painter.drawLine(links, y - 10, rechts, y - 10)
        painter.drawLine(links, y + groesse + 10, rechts, y + groesse + 10)

        # Figuren nur im Tunnel zeichnen, damit sie nicht über Rahmen und Banner laufen
        painter.save()
        painter.setClipRect(QRect(links, y - 8, rechts - links, groesse + 16))

        # Sterne vor dem Roboter sind noch nicht eingesammelt
        for x in range(links + 14, rechts - groesse, 36):
            if x > self.anim_x + groesse / 2:
                painter.drawImage(QRectF(x, y, groesse, groesse), self.punkt_img)

        # Leichtes Auf und Ab, damit der Roboter schwebt
        wippen = 2 * math.sin(self.anim_tick / 4)
        painter.drawImage(QRectF(self.anim_x, y + wippen, groesse, groesse), self.spieler_img)
        for i, geist in enumerate(self.geister_img):
            gx = self.anim_x - 70 - i * 44
            hopsen = -abs(3 * math.sin(self.anim_tick / 3 + i))
            painter.drawImage(QRectF(gx, y + hopsen, groesse, groesse), geist)
        painter.restore()

    def eintraege_zeichnen(self, painter, start_y):
        self.eintrag_rects = []
        painter.setFont(self.schrift(40))
        fm = painter.fontMetrics()
        zeilen_hoehe = 64

        for i, (text, _, aktiv) in enumerate(self.eintraege):
            y = start_y + i * zeilen_hoehe
            text_breite = fm.horizontalAdvance(text)
            x = (self.BREITE - text_breite) // 2
            rect = QRect(x - 60, y, text_breite + 120, zeilen_hoehe - 8)
            self.eintrag_rects.append(rect)

            ausgewaehlt = i == self.auswahl and aktiv
            if not aktiv:
                farbe = GRAU
            elif ausgewaehlt:
                farbe = NEON
            else:
                farbe = WEISS

            painter.setPen(farbe)
            painter.drawText(rect, Qt.AlignCenter, text)

            if ausgewaehlt:
                # Roboter als Auswahlpfeil links und rechts
                s = 30
                cy = rect.center().y() - s // 2
                painter.drawImage(QRectF(x - 50, cy, s, s), self.cursor_img)
                painter.save()
                painter.translate(x + text_breite + 50, cy)
                painter.scale(-1, 1)
                painter.drawImage(QRectF(0, 0, s, s), self.cursor_img)
                painter.restore()

            if not aktiv:
                painter.setFont(self.schrift(13))
                painter.drawText(QRect(x + text_breite + 8, y + 6, 80, 20), Qt.AlignLeft, "LEER")
                painter.setFont(self.schrift(40))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Pixel-Grafiken scharf vergrößern
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

        painter.fillRect(self.rect(), HINTERGRUND)
        zeichne_sterne(painter, self.BREITE, self.HOEHE, seed=3)
        self.rahmen_zeichnen(painter)

        banner_hoehe = self.banner.height()
        painter.drawImage(50, 44, self.banner)

        self.animation_zeichnen(painter, 50 + banner_hoehe + 22)
        self.eintraege_zeichnen(painter, 50 + banner_hoehe + 90)

        # Highscore und Bedienhinweis unten
        bester = max(self.game.score.text, default=0)
        painter.setFont(self.schrift(20))
        painter.setPen(WEISS)
        painter.drawText(QRect(0, self.HOEHE - 120, self.BREITE, 30), Qt.AlignCenter,
                         f"HIGHSCORE  {bester}")

        painter.setFont(self.schrift(13, fett=False))
        painter.setPen(GRAU)
        painter.drawText(QRect(0, self.HOEHE - 72, self.BREITE, 24), Qt.AlignCenter,
                         "W / S  AUSWÄHLEN   ·   ENTER  BESTÄTIGEN   ·   ESC  BEENDEN")


if __name__ == "__main__":
    setze_app_id()

    app = QApplication(sys.argv)
    application = menu()
    application.show()
    sys.exit(app.exec_())
