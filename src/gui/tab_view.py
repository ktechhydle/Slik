from src.imports import *
from src.gui.tab import Tab
from src.gui.file_browser import FileBrowser


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

    def openTab(self, filename: str, insert=False):
        filename = os.path.abspath(filename)

        for tab in self._tabs:
            if tab.filename() == filename:
                index = self.indexOf(tab)
                if index == -1:
                    # tab exists in memory but not in QTabWidget, re-add it
                    name = os.path.basename(tab.filename())

                    if insert:
                        self.insertTab(self.currentIndex() + 1, tab, name)
                        self.setCurrentIndex(self.currentIndex() + 1)
                    else:
                        self.addTab(tab, name)
                        self.setCurrentIndex(self.count() - 1)

                else:
                    # tab already exists in the widget; switch to it
                    self.setCurrentIndex(index)

                return

        # tab doesn't exist at all, create and add it
        tab = Tab(filename, self, self)
        name = os.path.basename(tab.filename())

        if insert:
            self.insertTab(self.currentIndex() + 1, tab, name)
            self.setCurrentIndex(self.currentIndex() + 1)
        else:
            self.addTab(tab, name)
            self.setCurrentIndex(self.count() - 1)

        self._tabs.append(tab)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.removeTab(index)
            self.defaultTab()

            return

        self.removeTab(index)

    def defaultTab(self):
        self.openTab('resources/default/start.md')

    def updateTab(self, old_name: str, new_name: str):
        for tab in self._tabs:
            current_name = os.path.basename(tab.filename())

            if current_name == old_name:
                if current_name in self._tabs:
                    self._tabs[self._tabs.index(current_name)] = os.path.basename(new_name)

                tab.setFileName(new_name)

    def showFileBrowser(self):
        self.file_browser.exec()

    def openProject(self, path: str):
        self.file_browser.setPath(path)
        self.clear()

    def tabs(self) -> list[str]:
        return self._tabs
