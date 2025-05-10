import os
import sys
import slik
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFontDatabase
from PyQt6.QtWidgets import QMainWindow, QSplitter, QApplication
from src.gui.message_dialog import MessageDialog
from src.gui.tab_view import TabView
from src.gui.terminal import Terminal


class Slik(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slik')
        self.setWindowIcon(QIcon('resources/icons/logos/slik_icon.svg'))
        self.resize(1000, 800)

        self.createUI()

    def createUI(self):
        splitter = QSplitter()
        splitter.setHandleWidth(3)
        splitter.setOrientation(Qt.Orientation.Vertical)

        self.tab_view = TabView()
        self.tab_view.openProject(os.path.abspath('./'))
        self.tab_view.defaultTab()
        self.tab_view.openTab('test.py', insert=True)

        self.terminal = Terminal(os.path.abspath('./'), self)

        splitter.addWidget(self.tab_view)
        splitter.addWidget(self.terminal)
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
