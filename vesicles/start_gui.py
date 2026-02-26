from PySide6.QtWidgets import QApplication
import sys

from multiprocessing import freeze_support


def start_gui():
    freeze_support()

    app = QApplication(sys.argv)


    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    start_gui()