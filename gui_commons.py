#this widget contains layouts that are used in multiple tabs.
#They are stored here to avoid circular imports -jk

import sys
from PySide6.QtWidgets import  QApplication
import matplotlib as mpl

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvas)

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QToolButton, QTextBrowser,
    QLabel, QSizePolicy, QGridLayout, QDialog, QPushButton, QTextEdit, QDialog
)


class ImageCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.figure = mpl.figure.Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)  # , figsize=(2, 2))
        super().__init__(self.figure)
        self.parent = parent

        # self.axis = self.figure.gca()

        self._file = None

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        if file is not None and file is not self._file:
            self._file = file
            self.refresh()
        elif file is None:
            self._file = None
            self.figure.clf()
            self.draw()

    def refresh(self):
        self.figure.clf()
        self._file.movie.determine_spatial_background_correction(use_existing=True)
        self._file.show_coordinates_in_image(figure=self.figure)
        self.draw()


class HelpDialog(QDialog):
    def __init__(self, parent=None, help_text=""):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.resize(600, 600)

        layout = QVBoxLayout(self)

        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        self.text.setHtml(help_text)

        layout.addWidget(self.text)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout.addWidget(self.text)
        layout.addWidget(close_button)