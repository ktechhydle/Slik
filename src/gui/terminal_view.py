import os
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtWidgets import QTabWidget, QToolButton
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

        self.tabCloseRequested.connect(self.closeTerminal)

        self.createActions()
        self.createUI()

    def clear(self):
        super().clear()

        self.newTerminal()

    def createUI(self):
        new_terminal_btn = QToolButton()
        new_terminal_btn.setObjectName('actionButton')
        new_terminal_btn.setIcon(QIcon('resources/icons/ui/plus_icon.svg'))
        new_terminal_btn.clicked.connect(self.newTerminal)

        self.setCornerWidget(new_terminal_btn)

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
