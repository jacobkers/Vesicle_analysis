

import platform
import property_merger

import sys
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QTreeView, QApplication, QMainWindow, \
    QPushButton, QTabWidget, QTableWidget, QComboBox, QLineEdit, QLabel
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon
from PySide6.QtCore import Qt
import matplotlib as mpl

from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from gui_commons import ImageCanvas,HelpDialog
from gui_results_view_widget import ResultsWidget
class MainWindow(QMainWindow):

    def __init__(self, main_path=None):
        super().__init__()
        system = platform.system()
        self.update = True

        # imagery (currently goes to extraction tab)
        self.image_canvas = ImageCanvas(self, width=4, height=4, dpi=100)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        image_toolbar = NavigationToolbar(self.image_canvas, self)
        image_layout = QVBoxLayout()
        image_layout.addWidget(image_toolbar)
        image_layout.addWidget(self.image_canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.image = QWidget()
        self.image.setLayout(image_layout)


        #main buttons:
        main_help_button = QPushButton('Read me')
        main_help_button.clicked.connect(self.show_main_help)

        import_vesicles_button = QPushButton('import excel')
        import_vesicles_button.setToolTip("press to re-import excel")
        import_vesicles_button.clicked.connect(self.import_excel)

        process_vesicles_button = QPushButton('(re)process')
        process_vesicles_button.setToolTip("press to update project data")
        process_vesicles_button.clicked.connect(self.update_movies)

        export_vesicles_button = QPushButton('export to vesicles.xls')
        export_vesicles_button.setToolTip("press to save to vesicles.xls")
        export_vesicles_button.clicked.connect(self.export_vesicles)

        start_tab_layout=QVBoxLayout()

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)
        tabs.setDocumentMode(True)

        tab0 = QWidget(self)
        tab0.setLayout(start_tab_layout)
        tabs.addTab(tab0, 'Pictures')
        kinetics = ResultsWidget(parent=self)
        tabs.addTab(kinetics, 'Graphs')
        tabs.currentChanged.connect(self.setTabFocus)


        left_layout = QVBoxLayout()
        left_layout.addWidget(main_help_button)
        left_layout.addWidget(import_vesicles_button)
        left_layout.addWidget(process_vesicles_button)
        left_layout.addWidget(export_vesicles_button)


        #build main panel
        right_layout = QHBoxLayout()
        #right_layout.addWidget(tabs)

        super_layout = QHBoxLayout()
        super_layout.addLayout(left_layout)
        super_layout.addLayout(right_layout)

        widget = QWidget()
        widget.setLayout(super_layout)
        self.setCentralWidget(widget)
        self.show()

    def update_button_color(self,button):
        if property_merger.any_dirty():
            button.setStyleSheet("background-color: red;")
        else:
            button.setStyleSheet("background-color: lightgreen;")

    def keyPressEvent(self, e):
        self.traces.keyPressEvent(e)

    def setTabFocus(self, e):
        if e == 0:
            self.image.setFocus()
        if e == 1:
            #self.traces.setFocus()
            dum=1


    def import_excel(self):
        property_merger.import_excel()
        print("imported vesicle data:")

    def update_movies(self):
        property_merger.process_movies()
        print("current data base contents:")
        property_merger.show_movies_df()


    def export_vesicles(self):
        property_merger.export_to_excel()
        print(f"exported vesicle data")


    def show_main_help(self):
        help_text = """
                <html>
                  <body style="font-family: sans-serif; font-size: 10pt;">

                    <h2>Welcome</h2>

                    <p>
                      This gui syncs user-based Excel entries with an database and an analysis pipeline. 
                      It is intended to allow a user to adapt settings and annotate on various data levels,
                      for example, to select and deselect movies or vesicles
                    </p>
                     
                     <p>

                        <ul>
                          <li>edit the various excel levels</li>
                          <li>press the corresponding update button</li>
                          <li></li>
                        </ul>
                     </p>   
                    
                    <p>   
                    code will automatically add changes, re-analyze data if necessary
                    and export updated results back to the Excels
                    </p>
                    
                    <p>
                      code is here:
                      <a href="https://github.com/jacobkers/">
                        Vesicle code
                      </a>.
                    </p>

                    <h3>Tips</h3>

                    <p>
                      <ul>
                        <li>Hover over buttons for help notes.</li>
                        <li>Find more detailed info under the 'Help' buttons per tab</li>
                    </ul>

                    </p>

                  </body>
                </html>
                """
        self.help_dialog = HelpDialog(self, help_text)
        # dialog.exec_()  # modal
        self.help_dialog.show()

if __name__ == '__main__':
    from multiprocessing import Process, freeze_support
    freeze_support()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


