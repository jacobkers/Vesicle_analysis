import sys
import json
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QTreeView, QApplication, QMainWindow, \
    QPushButton, QTabWidget, QTableWidget, QComboBox, QLineEdit
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from gui.common_layouts import ImageCanvas,Expander,HelpDialog

from matplotlib.figure import Figure
import numpy as np

from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class KineticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # imagery
        self.fig_kinetics = Figure(figsize=(5, 3))
        self.dwell_kinetics_canvas = FigureCanvas(self.fig_kinetics)



        #main
        dwell_help_button = QPushButton('Help!')
        dwell_help_button.clicked.connect(self.show_dwell_help)

        dwell_export_button = QPushButton('Export')

        dwell_controls_layout = QVBoxLayout()
        dwell_controls_layout.addWidget(dwell_help_button)
        dwell_controls_layout.addWidget(dwell_export_button)

        dwell_controls = QWidget()
        dwell_controls.setLayout(dwell_controls_layout)

        dwell_times_tab_layout = QHBoxLayout()
        dwell_times_tab_layout.addWidget(dwell_controls)
        dwell_times_tab_layout.addWidget(self.dwell_kinetics_canvas)


        #other
        other_graph_layout = QHBoxLayout()
        #other_graph_layout.addWidget(box2)


        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)
        tabs.setDocumentMode(True)

        tab1 = QWidget(self)
        tab1.setLayout(dwell_times_tab_layout)
        tabs.addTab(tab1, 'Dwell Time')
        tab2 = QWidget(self)
        tab2.setLayout(other_graph_layout)
        tabs.addTab(tab2, 'Other')


        self.kinetics_widget = QWidget()
        kinetics_layout = QHBoxLayout()
        kinetics_layout.addWidget(tabs)
        #self.kinetics_widget.setLayout(kinetics_layout)
        self.setLayout(kinetics_layout)


    def show_dwell_help(self):

        help_text = """
                <html>
                  <body style="font-family: sans-serif; font-size: 10pt;">
                
                    <h2>Dwell Times</h2>
                
                    <p>
                      Choose which variable and method should be used for the dwell time analysis.
                    </p>
                
                    <ul>
                      <li>Select the variable for dwell time extraction</li>
                      <li>Select the analysis method</li>
                    </ul>
                
                    <p>
                      For more help, see the
                      <a href="https://papylio.readthedocs.io/en/stable/user_guide/dwell_time_analysis/index.html">
                        dwell time analysis documentation
                      </a>.
                    </p>
                
                    <h3>Example</h3>
                
                    <p>
                      Settings examples can be found in the documentation.
                    </p>
                
                  </body>
                </html>
                """
        self.help_dialog = HelpDialog(self, help_text)
        # dialog.exec_()  # modal
        self.help_dialog.show()


