import os

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTabWidget, QWidget
from src.gui.tab import Tab


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self._tabs = []
        self._project_dir = ''

        self.tabCloseRequested.connect(self.closeTab)

    def clear(self, no_default=False):
        super().clear()

        self._tabs.clear()

        if no_default:
            return

        self.defaultTab()

    def openTab(self, filename: str, insert=False):
        filename = os.path.abspath(filename)

        for tab in self._tabs:
            if tab.filename() == filename:
                index = self.indexOf(tab)
                if index == -1:
                    # tab exists in memory but not in widget, re-add it
                    name = tab.basename()

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
        name = tab.basename()

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

    def updateTab(self, old_name: str, new_name: str):
        old_name = os.path.abspath(old_name)

        for i, tab in enumerate(self._tabs):
            if tab.filename() == old_name:
                if new_name and os.path.exists(new_name):
                    tab.setFileName(os.path.abspath(new_name))
                    self._tabs[i] = tab

                else:
                    # tab filename is deleted, remove it
                    self.closeTab(i)

                break

    def defaultTab(self):
        self.openTab('resources/default/start.md')

    def setProjectDir(self, path: str):
        self._project_dir = path

        readme_path = f'{path}/README.md'

        if os.path.exists(readme_path):
            self.clear(no_default=True)
            self.openTab(readme_path)

        else:
            self.clear()

    def tabs(self) -> list[QWidget]:
        return self._tabs

    def projectDir(self) -> str:
        return self._project_dir

    def currentTab(self) -> Tab:
        return self.widget(self.currentIndex())
