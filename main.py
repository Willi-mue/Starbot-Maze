from logic.logic import *

class menu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Menu')

        self.scale = 2
        self.game_hoehe = 1080
        self.game_breite = 1920

        self.game = pacman(self.game_hoehe, self.game_breite, "game/map.txt", "logic/highscore.txt")

        self.setWindowIcon(QIcon("images/icon.png"))

        self.tabWidget = QTabWidget(self)

        self.tabWidget.setGeometry(0, 0, 600, 400)

        self.setStyleSheet('''
                       QTabWidget::tab-bar {
                           alignment: left;
                       }''')

        self.title1 = QLabel(self)
        self.title1.setGeometry(280, 140, 300, 20)

        self.button1 = QPushButton(self)
        self.button1.setGeometry(50, 50, 200, 60)
        self.button1.setText("Start")
        self.button1.clicked.connect(self.start_button)

        self.button2 = QPushButton(self)
        self.button2.setGeometry(50, 150, 200, 60)
        self.button2.setText("Load")
        self.button2.clicked.connect(self.load_button)

        self.button3 = QPushButton(self)
        self.button3.setGeometry(200, 300, 200, 60)
        self.button3.setText("Exit")
        self.button3.clicked.connect(self.end_game)

        self.combo = QComboBox(self)
        self.combo.setGeometry(340, 80, 150, 40)
        self.combo.addItem("1920 1080")
        self.combo.addItem("3840 2160")
        self.combo.activated[str].connect(self.onChanged)

    def onChanged(self, text):
        self.game_hoehe = int(text.split()[1])
        self.game_breite = int(text.split()[0])
        if self.game_breite == 3840:
            self.scale = 1
            self.game = pacman(self.game_hoehe, self.game_breite, "game/map.txt", "logic/highscore.txt")

    def start_button(self):
        self.game.show()
        self.hide()

    def end_game(self):
        sys.exit()

    def load_button(self):
        pass


    
if __name__ == "__main__":
    my_app_id = 'by_Müller_Willi.MyPacman.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

    app = QApplication(sys.argv)
    application = menu()
    application.show()
    sys.exit(app.exec_())