import os
import slik
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QWidget
from PyQt6.Qsci import QsciAPIs, QsciScintilla
from src.gui.message_dialog import MessageDialog
from src.gui.tab import Tab


class TabContentIndexer(QThread):
    finished = pyqtSignal(list)

    def __init__(self, tabs: list[Tab]):
        super().__init__()

        self._tabs = tabs
        self._results = []

    def run(self):
        for tab in self._tabs:
            old_contents = tab.editor().text()
            new_contents = slik.read(tab.filename()) if os.path.exists(tab.filename()) else old_contents

            if old_contents != new_contents:
                self._results.append((tab, new_contents))

        self.finished.emit(self._results)

        self._results.clear()


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
        tab = self.widget(index)

        if tab and not tab.saved():
            message = MessageDialog('Unsaved Changes',
            f'File {tab.basename()} has unsaved changes. Do you want '
            'to save them?',
            (MessageDialog.YesButton, MessageDialog.NoButton),
            self)
            message.exec()

            if message.result() == MessageDialog.Accepted:
                tab.save()

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

                    if tab in self._tabs:
                        self._tabs.remove(tab)

                break

    def updateTabContents(self):
        if hasattr(self, '_tab_content_indexer'):
            self._tab_content_indexer.wait() # wait for thread to finish

        self._tab_content_indexer = TabContentIndexer(self._tabs)

        def update_tab(results: list[tuple[Tab, str]]):
            if results:
                for tab, contents in results:
                    if tab.saved(): # the tab is saved, so we can change it's contents
                        tab.editor().setText(contents, preserve=True)

        self._tab_content_indexer.finished.connect(update_tab)
        self._tab_content_indexer.start()

    def defaultTab(self):
        self.openTab('resources/info/start.md')

    def shortcutsTab(self):
        self.openTab('resources/info/shortcuts.md')

    def setProjectDir(self, directory: str):
        if directory != self._project_dir:
            self._project_dir = directory

            readme_path = f'{directory}/README.md'

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
