import os
import slik
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QTabWidget, QComboBox
from PyQt6.QtGui import QAction, QKeySequence
from src.managers.terminal_manager import TerminalManager
from src.gui.file_searcher import FileSearcher
from src.gui.message_dialog import MessageDialog
from src.gui.tab_view import TabView
from src.gui.file_browser import FileBrowser


class ProjectIndexer(QThread):
    def __init__(self):
        super().__init__()

        self._project_dir = ''
        self._result = []

    def run(self):
        self._result = slik.index(self._project_dir)

        self.finished.emit()

    def setProjectDir(self, path: str):
        self._project_dir = path

    def projectDir(self) -> str:
        return self._project_dir

    def result(self) -> list[tuple[str, str]]:
        return self._result


class ProjectManager:
    def __init__(self, tab_view: QTabWidget, terminal_manager: TerminalManager, run_type_selector: QComboBox, python_path_selector: QComboBox):
        self._tab_view = tab_view
        self._terminal_manager = terminal_manager
        self._run_type_selector = run_type_selector
        self._python_path_selector = python_path_selector
        self._project_indexer = ProjectIndexer()
        self._project_indexer.finished.connect(self.indexFinished)
        self._old_index = []

        self.createDialogs()
        self.createActions()

    def createDialogs(self):
        self._file_searcher = FileSearcher(self._tab_view, self._tab_view)

        self._file_browser = FileBrowser('', self._tab_view, self._tab_view)
        self._file_browser.projectDirChanged.connect(self._terminal_manager.setProjectDir)
        self._file_browser.projectDirChanged.connect(self._tab_view.setProjectDir)
        self._file_browser.projectDirChanged.connect(self._file_searcher.setProjectDir)
        self._file_browser.projectDirChanged.connect(self._project_indexer.setProjectDir)
        self._file_browser.projectDirChanged.connect(self._python_path_selector.getPythonPath)
        self._file_browser.projectDirChanged.connect(self.indexProject)
        self._file_browser.projectChanged.connect(self._tab_view.updateTabContents)
        self._file_browser.projectChanged.connect(self.updateProject)

    def createActions(self):
        save_action = QAction('Save', self._tab_view)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(lambda: self._tab_view.currentTab().save())

        toggle_collapse_action = QAction('Toggle Collapse', self._tab_view)
        toggle_collapse_action.setShortcut(QKeySequence('Ctrl+F'))
        toggle_collapse_action.triggered.connect(lambda: self._tab_view.currentTab().editor().foldAll(True))

        file_browser_action = QAction('File Browser', self._tab_view)
        file_browser_action.setShortcut(QKeySequence('Ctrl+Q'))
        file_browser_action.triggered.connect(self.showFileBrowser)

        file_searcher_action = QAction('File Searcher', self._tab_view)
        file_searcher_action.setShortcut(QKeySequence('Ctrl+Shift+Q'))
        file_searcher_action.triggered.connect(self.showFileSearcher)

        run_project_action = QAction('Run', self._tab_view)
        run_project_action.setShortcut(QKeySequence('Ctrl+R'))
        run_project_action.triggered.connect(self.run)

        run_current_file_action = QAction('Run Current File', self._tab_view)
        run_current_file_action.setShortcut(QKeySequence('Ctrl+Shift+R'))
        run_current_file_action.triggered.connect(self.runCurrent)

        new_terminal_action = QAction('New Terminal', self._tab_view)
        new_terminal_action.setShortcut(QKeySequence('Ctrl+N'))
        new_terminal_action.triggered.connect(self._terminal_manager.newTerminal)

        self._tab_view.addAction(save_action)
        self._tab_view.addAction(toggle_collapse_action)
        self._tab_view.addAction(file_browser_action)
        self._tab_view.addAction(file_searcher_action)
        self._tab_view.addAction(run_project_action)
        self._tab_view.addAction(run_current_file_action)
        self._tab_view.addAction(new_terminal_action)

    def showFileBrowser(self):
        self._file_browser.exec()

    def showFileSearcher(self):
        self._file_searcher.exec()

    def openProject(self, path: str):
        self._file_browser.setPath(path)

    def updateProject(self):
        self._old_index = self._project_indexer.result()
        self.indexProject()

    def indexProject(self):
        if self._project_indexer.isRunning():
            self._project_indexer.wait()

        self._project_indexer.start()

    def indexFinished(self):
        new_index_list = self._project_indexer.result()
        old_index_list = self._old_index

        old_index = dict(old_index_list)  # {filename: hash}
        new_index = dict(new_index_list)  # {filename: hash}

        renamed = []
        matched_old_files = set()
        matched_new_files = set()

        for old_name, old_hash in old_index.items():
            for new_name, new_hash in new_index.items():
                if old_hash == new_hash and old_name != new_name:
                    renamed.append((old_name, new_name))
                    matched_old_files.add(old_name)
                    matched_new_files.add(new_name)

                    break

        deleted_files = set(old_index.keys()) - matched_old_files - set(new_index.keys())

        for old_name, new_name in renamed:
            self._tab_view.updateTab(old_name, new_name)

        for deleted in deleted_files:
            self._tab_view.updateTab(deleted, '')

        self._old_index = new_index_list

    def run(self):
        command = self.parseRunConfig()

        if command:
            self._terminal_manager.terminalFromCommand(command)

    def runCurrent(self):
        file = self._tab_view.currentTab().filename()

        if file.endswith('.py'):
            self._terminal_manager.terminalFromCommand(f'{self._python_path} {file}')

        elif file.endswith('.rs'):
            if os.path.exists(f'{self.projectDir()}/Cargo.toml'):
                self._terminal_manager.terminalFromCommand('cargo run')

            else:
                message = MessageDialog("No 'Cargo.toml' File",
                                        "The project runner couldn't find a 'Cargo.toml' entry point.",
                                        (MessageDialog.OkButton,),
                                        self._tab_view)
                message.exec()

    def parseRunConfig(self) -> str | None:
        config = self._run_type_selector.runConfig()
        args = config.split('+')
        command = ''

        for arg in args:
            if arg == 'PYTHONPATH':
                arg = self._python_path_selector.pythonPath()

            elif arg == 'CURRENTFILEPY':
                if self._tab_view.currentTab().filename().endswith('.py'):
                    arg = self._tab_view.currentTab().filename()

                else:
                    return

            elif arg == 'MAINPY':
                arg = 'main.py'

                if not os.path.exists(f'{self.projectDir()}/{arg}'):
                    message = MessageDialog("No 'main.py' File",
                                            "The project runner couldn't find a 'main.py' entry point.",
                                            (MessageDialog.OkButton,),
                                            self._tab_view)
                    message.exec()

                    return

            command += arg + ' '

        return command.strip()

    def tabView(self) -> TabView:
        return self._tab_view

    def terminalManager(self) -> TerminalManager:
        return self._terminal_manager

    def fileBrowser(self) -> FileBrowser:
        return self._file_browser

    def projectDir(self) -> str:
        return self._file_browser.path()