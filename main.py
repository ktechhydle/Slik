import os
import sys
import slik
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFontDatabase
from PyQt6.QtWidgets import QMainWindow, QSplitter, QApplication
from src.managers.terminal_manager import TerminalManager
from src.managers.project_manager import ProjectManager
from src.gui.configure_bar import ConfigureBar
from src.gui.message_dialog import MessageDialog
from src.gui.tab_view import TabView


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
        self.configure_bar = ConfigureBar()
        self.tab_view.setCornerWidget(self.configure_bar)

        self.terminal_manager = TerminalManager()
        self.project_manager = ProjectManager(self.tab_view,
                                              self.terminal_manager,
                                              self.configure_bar.runTypeSelector(),
                                              self.configure_bar.pythonPathSelector())
        self.project_manager.openProject(os.path.abspath('.'))

        splitter.addWidget(self.tab_view)
        self.setCentralWidget(splitter)


def main():
    app = QApplication(sys.argv)
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
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
