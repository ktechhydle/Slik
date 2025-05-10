import os
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QTabWidget

from managers.project_manager import ProjectManager
from src.gui.terminal import Terminal


class TerminalView(QTabWidget):
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self._project_manager = project_manager

        self.tabCloseRequested.connect(self.closeTerminal)

        self.createActions()

    def clear(self):
        super().clear()

        self.newTerminal()

    def createActions(self):
        new_terminal_action = QAction('New Terminal', self)
        new_terminal_action.setShortcut(QKeySequence('Ctrl+N'))

        self.addAction(new_terminal_action)

    def newTerminal(self):
        self.openTerminal(self._project_manager.projectDir())

    def openTerminal(self, cwd: str):
        terminal = Terminal(cwd, self)

        self.addTab(terminal, 'Local')

    def closeTerminal(self, index: int):
        if self.count() == 1:
            self.removeTab(index)
            self.newTerminal()

            return

        self.removeTab(index)
