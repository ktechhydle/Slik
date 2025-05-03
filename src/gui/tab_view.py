from src.imports import *
from src.gui.tab import Tab


class StartPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        self.createUI()

    def createUI(self):
        welcome_label = QLabel('<h1>Welcome to Slik!</h1>')
        help_label = QLabel('To get started, open a file with <code>Ctrl+Q</code>')

        self.layout().addStretch()
        self.layout().addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(help_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout().addStretch()


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.addTab(StartPage(), 'Start')
            self.removeTab(index - 1)

        self.removeTab(index)
        self.update()
