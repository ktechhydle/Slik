import os
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtWidgets import QTabWidget, QToolButton, QPushButton
from src.gui.terminal import Terminal
from src.gui.message_dialog import MessageDialog
from src.managers.project_manager import ProjectManager


class TerminalView(QTabWidget):
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self._project_manager = project_manager
        self._project_manager.fileBrowser().projectDirChanged.connect(self.clear)

        self.tabBar().tabBarDoubleClicked.connect(self.newTerminal)
        self.tabCloseRequested.connect(self.closeTerminal)

    def clear(self):
        super().clear()

        self.newTerminal()

    def newTerminal(self):
        self.openTerminal(self._project_manager.projectDir())

    def openTerminal(self, cwd: str):
        terminal = Terminal(cwd, self)

        self.insertTab(self.currentIndex() + 1, terminal, 'Local')
        self.setCurrentIndex(self.indexOf(terminal))

    def closeTerminal(self, index: int):
        if self.count() == 1:
            terminal = self.widget(index)

            if terminal.hasCurrentProcess():
                message = MessageDialog('Quit Process',
                                        'A process is currently running in this '
                                                        'terminal. Do you want to close it?',
                                        (MessageDialog.YesButton, MessageDialog.NoButton),
                                        self)
                message.exec()

                if not message.result() == MessageDialog.Accepted:
                    return

                else:
                    terminal.quit()

            self.removeTab(index)
            self.newTerminal()

            return

        self.removeTab(index)
