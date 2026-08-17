

import platform
import gui_property_merger
import os
import sys
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QTreeView, QApplication, QMainWindow, \
    QPushButton, QTabWidget, QFileDialog, QComboBox, QLineEdit, QLabel
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

        self.movies_in = None
        self.path_in = None
        self.vesicles_out=None
        self.database_file=None

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

        choose_data_button = QPushButton("Choose data file")
        choose_data_button.clicked.connect(self.choose_data_file)

        show_vesicles_db_button = QPushButton('Show database')
        show_vesicles_db_button.setToolTip("display current database contents")
        show_vesicles_db_button.clicked.connect(self.show_database)

        import_vesicles_button = QPushButton('Import Excel')
        import_vesicles_button.setToolTip("press to re-import excel")
        import_vesicles_button.clicked.connect(self.import_excel)

        #process & diagnose
        process_layout=QHBoxLayout()
        process_vesicles_button = QPushButton('Process + Graphs')
        process_vesicles_button.setToolTip("press to update project data")
        process_vesicles_button.clicked.connect(self.update_movies)
        self.pic_format_button= QComboBox()
        self.pic_format_button.addItems(['png', 'jpg', 'svg', 'none'])
        process_layout.addWidget(process_vesicles_button)
        process_layout.addWidget(self.pic_format_button)

        #export of excel
        export_layout=QHBoxLayout()
        export_vesicles_button = QPushButton('Export Excel')
        export_vesicles_button.setToolTip("press to save to vesicles.xls")
        export_vesicles_button.clicked.connect(self.export_vesicles)
        self.export_options_button = QComboBox()
        self.export_options_button.addItems(['all', 'selection'])
        export_layout.addWidget(export_vesicles_button)
        export_layout.addWidget(self.export_options_button)

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
        #tabs.currentChanged.connect(self.setTabFocus)

        left_layout = QVBoxLayout()
        left_layout.addWidget(main_help_button)
        left_layout.addWidget(choose_data_button)
        left_layout.addWidget(show_vesicles_db_button)
        left_layout.addWidget(import_vesicles_button)
        left_layout.addLayout(process_layout)
        left_layout.addLayout(export_layout)


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


    def import_excel(self):
        gui_property_merger.import_excel(self.database_file,self.movies_in)
        print("imported vesicle data")

    def show_database(self):
        print("current vesicle data:")
        gui_property_merger.show_movies_df(self.database_file)
        print("<--current vesicle data")

    def update_movies(self):
        pic_format=self.pic_format_button.currentText()
        gui_property_merger.process_movies(db_file=self.database_file, pic_format=pic_format)
        print("processed & updated database")

    def export_vesicles(self):
        export_option=self.export_options_button.currentText()
        gui_property_merger.export_to_excel(db_file=self.database_file, vesicles_out=self.vesicles_out, export_option=export_option)
        print(f"exported vesicle data")

    def choose_data_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select data overview file",
            "",
            "Excel files (*.xlsx);;All files (*)"
        )

        if filename:
            self.movies_in = filename
            self.path_in = os.path.dirname(filename)
            self.vesicles_out = os.path.join(self.path_in, "vesicles_out.xlsx")
            self.database_file = os.path.join(self.path_in, "project.db")
            print("Selected file:", self.movies_in)
            print("Input path:", self.path_in)

    def show_main_help(self):
        help_text = """
                <html>
                  <body style="font-family: sans-serif; font-size: 10pt;">

                    <h2>VesicleTool</h2>

                    <p>
                      This gui syncs user-based Excel entries with a database and an analysis pipeline. 
                      It is intended to allow a user to adapt settings and annotate on various data levels,
                      for example, to select and deselect movies or vesicles
                    </p>
                     
                     <p>

                        <ul>
                          <li> Set up your paths and files in the 'gui_config_experiment' file</li>
                          <li> Edit the various excel entries and set selection with 'use_it'=1</li>
                          <li>'Show database' shows current contents of the 'DB' .db file </li>
                          <li>'Import Excel' overwrites all selected DB rows  </li>
                          <li>'Process' analyzes and stores data with all selected DB rows </li>
                          <li> During processing, graphics are saved in the specified format field </li>
                          <li> 'Export Excel' saves either all or the selected rows </li>
                        </ul>
                     </p>   
                    
                    <p>   
                    VesicleTool will automatically add changes, re-analyze data if necessary
                    and export updated results back to the Excels
                    </p>
                    
                    <p>
                      Repository:
                      <a href="https://github.com/jacobkers/CD23_vesicles/">
                        Vesicle code
                      </a>.
                    </p>

                    <h3>Tips</h3>

                    <p>
                      <ul>
                        <li>Hover over buttons for help notes.</li>
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


