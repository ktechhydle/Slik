import slik
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QTabWidget
from src.gui.tab_view import TabView
from src.gui.terminal_view import TerminalView
from src.gui.file_browser import FileBrowser


class ProjectManager:
    def __init__(self, tab_view, terminal_view):
        self._tab_view = tab_view
        self._terminal_view = terminal_view

        self._project = {}

        self.createDialogs()
        self.createActions()

    def createDialogs(self):
        self._file_browser = FileBrowser('', self._tab_view, self._tab_view)
        self._file_browser.projectDirChanged.connect(self._terminal_view.setProjectDir)
        self._file_browser.projectDirChanged.connect(self._tab_view.setProjectDir)
        self._file_browser.projectChanged.connect(self.updateProject)

    def createActions(self):
        save_action = QAction('Save', self._tab_view)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(lambda: self._tab_view.currentWidget().save())

        toggle_collapse_action = QAction('Toggle Collapse', self._tab_view)
        toggle_collapse_action.setShortcut(QKeySequence('Ctrl+F'))
        toggle_collapse_action.triggered.connect(lambda: self._tab_view.currentWidget().editor().foldAll(True))

        file_browser_action = QAction('File Browser', self._tab_view)
        file_browser_action.setShortcut(QKeySequence('Ctrl+Q'))
        file_browser_action.triggered.connect(self.showFileBrowser)

        run_project_action = QAction('Run', self._tab_view)
        run_project_action.setShortcut(QKeySequence('Ctrl+R'))
        run_project_action.triggered.connect(self._tab_view.run)

        run_current_file_action = QAction('Run Current File', self._tab_view)
        run_current_file_action.setShortcut(QKeySequence('Ctrl+Shift+R'))
        run_current_file_action.triggered.connect(self._tab_view.runCurrent)

        self._tab_view.addAction(save_action)
        self._tab_view.addAction(toggle_collapse_action)
        self._tab_view.addAction(file_browser_action)
        self._tab_view.addAction(run_project_action)
        self._tab_view.addAction(run_current_file_action)

    def showFileBrowser(self):
        self._file_browser.exec()

    def openProject(self, path: str):
        self._file_browser.setPath(path)

    def updateProject(self):
        # detect the changed files/dirs and update tabs based on changes
        pass

    def tabView(self) -> TabView:
        return self._tab_view

    def terminalView(self) -> TerminalView:
        return self._terminal_view

    def fileBrowser(self) -> FileBrowser:
        return self._file_browser

    def projectDir(self) -> str:
        return self._file_browser.path()