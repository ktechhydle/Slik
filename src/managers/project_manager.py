import slik
from src.gui.file_browser import FileBrowser


class ProjectManager:
    def __init__(self, tab_view):
        self.tab_view = tab_view

        self._project = {}

        self.createDialogs()

    def createDialogs(self):
        self._file_browser = FileBrowser('', self.tab_view, self.tab_view)
        self._file_browser.projectDirChanged.connect(print)
        self._file_browser.projectChanged.connect(self.updateProject)

    def showFileBrowser(self):
        self._file_browser.exec()

    def openProject(self, path: str):
        self._file_browser.setPath(path)

    def updateProject(self):
        # detect the changed files/dirs and update tabs based on changes
        pass

    def fileBrowser(self) -> FileBrowser:
        return self._file_browser

    def projectDir(self) -> str:
        return self._file_browser.path()