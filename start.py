from start_menu import *

my_app_id = 'by_Müller_Willi.MyPacman.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


def main():
    app = QApplication(sys.argv)
    application = menu()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
