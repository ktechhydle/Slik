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

    def filename(self) -> str:
        return 'Start'


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self.tabs = []

        self.tabCloseRequested.connect(self.closeTab)

        self.createActions()

    def createActions(self):
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(lambda: self.currentWidget().save())

        toggle_collapse_action = QAction('Toggle Collapse', self)
        toggle_collapse_action.setShortcut(QKeySequence('Ctrl+F'))
        toggle_collapse_action.triggered.connect(lambda: self.currentWidget().editor().foldAll(True))

        self.addAction(save_action)
        self.addAction(toggle_collapse_action)

    def updateTabs(self):
        for i in range(self.count()):
            tab = self.widget(i)

    def addTab(self, widget: Tab):
        if widget in self.tabs:
            self.removeTab(self.indexOf(widget))
            super().addTab(widget, widget.filename())

            return

        self.tabs.append(widget)

        super().addTab(widget, widget.filename())

    def openCachedTab(self, filename: str):
        for widget in self.tabs:
            if widget.filename() == filename:
                self.addTab(widget, widget.filename())

    def closeTab(self, index: int):
        if self.count() == 1:
            self.addTab(StartPage())
            self.removeTab(index - 1)

        self.removeTab(index)
        self.update()
