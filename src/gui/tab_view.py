from src.imports import *
from src.gui.tab import Tab
from src.gui.file_browser import FileBrowser


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

        self._tabs = []

        self.tabCloseRequested.connect(self.closeTab)

        self.createUI()
        self.createActions()

    def addTab(self, widget: Tab, insert=False, ignore=False):
        if widget.filename() not in self._tabs:
            if insert:
                self.insertTab(self.currentIndex() + 1, widget, os.path.basename(widget.filename()))
                self.setCurrentIndex(self.currentIndex() + 1)

            else:
                super().addTab(widget, widget.filename() if ignore else os.path.basename(widget.filename()))
                self.setCurrentIndex(self.count() + 1)

            self._tabs.append(widget.filename())

    def clear(self):
        super().clear()

        self._tabs.clear()
        self.defaultTab()

    def createUI(self):
        self.file_browser = FileBrowser('', self, self)

    def createActions(self):
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(lambda: self.currentWidget().save())

        toggle_collapse_action = QAction('Toggle Collapse', self)
        toggle_collapse_action.setShortcut(QKeySequence('Ctrl+F'))
        toggle_collapse_action.triggered.connect(lambda: self.currentWidget().editor().foldAll(True))

        file_browser_action = QAction('File Browser', self)
        file_browser_action.setShortcut(QKeySequence('Ctrl+Q'))
        file_browser_action.triggered.connect(self.showFileBrowser)

        self.addAction(save_action)
        self.addAction(toggle_collapse_action)
        self.addAction(file_browser_action)

    def defaultTab(self):
        self.addTab(StartPage(), ignore=True)

    def closeTab(self, index: int):
        widget = self.widget(index)

        if self.count() == 1:
            self.removeTab(index)

            if widget.filename() in self._tabs:
                self._tabs.remove(widget.filename())

            self.defaultTab()

            return

        if widget.filename() in self._tabs:
            self._tabs.remove(widget.filename())

        self.removeTab(index)

    def updateTab(self, old_name: str, new_name: str):
        for i in range(self.count()):
            tab = self.widget(i)
            current_name = os.path.basename(tab.filename())

            if current_name == old_name:
                if current_name in self._tabs:
                    self._tabs[self._tabs.index(current_name)] = os.path.basename(new_name)

                self.setTabText(i, os.path.basename(new_name))
                tab.setFileName(new_name)

    def showFileBrowser(self):
        self.file_browser.exec()

    def openProject(self, path: str):
        self.file_browser.setPath(path)
        self.clear()

    def tabs(self) -> list[str]:
        return self._tabs
