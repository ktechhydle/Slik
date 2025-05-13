import os
import sys
import slik
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFontDatabase
from PyQt6.QtWidgets import QMainWindow, QSplitter, QApplication
from src.managers.project_manager import ProjectManager
from src.gui.message_dialog import MessageDialog
from src.gui.tab_view import TabView
from src.gui.terminal_view import TerminalView


class Slik(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slik')
        self.setWindowIcon(QIcon('resources/icons/logos/slik_icon.svg'))
        self.resize(1000, 800)

        self.createUI()

    def createUI(self):
        splitter = QSplitter()
        splitter.setHandleWidth(2)
        splitter.setOrientation(Qt.Orientation.Vertical)

        self.tab_view = TabView(self)
        self.terminal_view = TerminalView(self)

        self.project_manager = ProjectManager(self.tab_view, self.terminal_view)
        self.project_manager.openProject(os.path.abspath('.'))

        splitter.addWidget(self.tab_view)
        splitter.addWidget(self.terminal_view)
        self.setCentralWidget(splitter)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(slik.read('resources/stylesheets/slik_dark.css'))

    QFontDatabase.addApplicationFont('resources/fonts/JetBrainsMono-Regular.ttf')

    window = Slik()
    window.show()

    # Crash handler
    def handle_exception(exctype, value, tb):
        message = MessageDialog('Error:(',
                      f'Slik encountered an error:\n\n{value}\n',
                      (MessageDialog.OkButton,),
                      window)
        message.exec()

        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
