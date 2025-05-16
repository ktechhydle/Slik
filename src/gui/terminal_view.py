from PyQt6.QtWidgets import QTabWidget
from src.gui.terminal import Terminal
from src.gui.message_dialog import MessageDialog


class TerminalView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self._project_dir = ''

        self.tabBar().tabBarDoubleClicked.connect(self.newTerminal)
        self.tabCloseRequested.connect(self.closeTerminal)

    def clear(self):
        for i in range(self.count()):
            self.closeTerminal(i)

        self.newTerminal()

    def newTerminal(self):
        self.openTerminal(self._project_dir)
        self.currentTerminal().currentInput().setFocus()

    def terminalFromCommand(self, command: str):
        if self.currentTerminal().hasCurrentProcess():
            # create a new terminal with the process
            terminal = Terminal(self._project_dir, self)

            self.addTab(terminal, 'Local')
            self.setCurrentIndex(self.indexOf(terminal))

            terminal.run(command)

        else:
            self.currentTerminal().run(command)

    def openTerminal(self, cwd: str):
        terminal = Terminal(cwd, self)

        self.insertTab(self.currentIndex() + 1, terminal, 'Local')
        self.setCurrentIndex(self.indexOf(terminal))

    def closeTerminal(self, index: int):
        terminal = self.widget(index)

        if terminal and terminal.hasCurrentProcess():
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

        if self.count() == 0:
            self.newTerminal()

    def setProjectDir(self, path: str):
        self._project_dir = path

        self.clear()

    def projectDir(self) -> str:
        return self._project_dir

    def currentTerminal(self) -> Terminal:
        return self.widget(self.currentIndex())

