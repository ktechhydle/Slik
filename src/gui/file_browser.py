from src.imports import *
from src.gui.tab import Tab


class FileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)

            if file_path.endswith('.py'):
                return QIcon('resources/icons/python_icon.svg')

            elif any(item in file_path for item in ('.rs', 'Cargo')):
                return QIcon('resources/icons/rust_icon.svg')

            elif os.path.isdir(file_path):
                return QIcon('resources/icons/folder_icon.svg')

            else:
                return QIcon('resources/icons/txt_icon.svg')

        return super().data(index, role)


class FileSystemWatcher(QFileSystemWatcher):
    def __init__(self, parent=None):
        super().__init__(parent)

    def changePath(self, path: str):
        self.clear()
        self.addPath(path)

    def clear(self):
        self.removePaths(self.directories())


class FileSystemViewer(QTreeView):
    def __init__(self, tab_view, file_browser, parent=None):
        super().__init__(parent)
        self.setAnimated(True)
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tab_view = tab_view
        self.file_browser = file_browser

        self.customContextMenuRequested.connect(self.showMenu)
        self.doubleClicked.connect(self.openFile)

    def showMenu(self, pos):
        if not hasattr(self, 'menu'):
            self.menu = QMenu(self.tab_view)

            new_file_action = QAction('New File', self)
            new_file_action.triggered.connect(self.newFile)

            new_dir_action = QAction('New Directory', self)
            new_dir_action.triggered.connect(self.newDir)

            rename_action = QAction('Rename...', self)
            rename_action.triggered.connect(self.renameSelected)

            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(self.removeSelected)

            self.menu.addAction(new_file_action)
            self.menu.addAction(new_dir_action)
            self.menu.addSeparator()
            self.menu.addAction(rename_action)
            self.menu.addSeparator()
            self.menu.addAction(delete_action)

        self.menu.exec(self.mapToGlobal(pos))

    def newFile(self):
        pass

    def newDir(self):
        pass

    def openFile(self, index: QModelIndex):
        model = self.model()
        filepath = model.filePath(index)

        if not model.isDir(index):
            self.tab_view.openTab(filepath, insert=True)

    def renameSelected(self):
        if len(self.selectedIndexes()) > 1:
            return

        index = self.currentIndex()

        if not index.isValid():
            return

        model = self.model()
        old_path = model.filePath(index)
        old_name = os.path.basename(old_path)
        dir_path = os.path.dirname(old_path)

        new_name, ok = QInputDialog.getText(self.tab_view, 'Rename', 'New name:', text=old_name)

        if ok and new_name:
            new_path = os.path.join(dir_path, new_name)
            self.tab_view.updateTab(old_name, new_path)

            try:
                os.rename(old_path, new_path)
                self.file_browser.updateFileBrowser()

            except Exception as e:
                raise e

    def removeSelected(self):
        indexes = self.selectedIndexes()

        if not indexes:
            return

        model = self.model()
        paths = list(set(model.filePath(index) for index in indexes if index.column() == 0))

        if not paths:
            return

        confirm = QMessageBox.warning(
            self.tab_view,
            'Remove',
            f'Are you sure you want to delete the {len(paths)} selected item(s)?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            for path in paths:
                try:
                    if os.path.isfile(path):
                        os.remove(path)

                    elif os.path.isdir(path):
                        shutil.rmtree(path)

                except Exception as e:
                    raise e


class FileBrowser(QMenu):
    def __init__(self, path: str, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.CoverWindow)
        self.setObjectName('fileBrowser')

        self._path = path
        self.tab_view = tab_view

        self.createUI()
        self.createWatcher()
        self.updateFileBrowser()

    def exec(self, pos=None):
        if pos:
            super().exec(pos)
            return

        parent_center = self.parent().rect().center()
        global_center = self.parent().mapToGlobal(parent_center)
        target_width = 600
        target_height = 400

        start_rect = QRect(
            global_center.x(),
            global_center.y(),
            1,
            1
        )
        end_rect = QRect(
            global_center.x() - target_width // 2,
            global_center.y() - target_height // 2,
            target_width,
            target_height
        )

        self.setGeometry(start_rect)
        self.container.setFixedSize(target_width, target_height)
        self.updateFileBrowser()

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

        self.show()

    def createUI(self):
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        action_container = QWidget()
        action_container.setLayout(QHBoxLayout())
        action_container.layout().setContentsMargins(0, 0, 0, 0)

        self._project_dir_label = QLabel('')
        open_project_btn = QPushButton('📁', self)
        open_project_btn.setObjectName('actionButton')
        open_project_btn.setFixedSize(25, 25)
        open_project_btn.clicked.connect(self.openProject)
        close_btn = QPushButton('❌', self)
        close_btn.setObjectName('actionButton')
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.animateClose)

        action_container.layout().addWidget(self._project_dir_label)
        action_container.layout().addStretch()
        action_container.layout().addWidget(open_project_btn)
        action_container.layout().addWidget(close_btn)

        self._file_view = FileSystemViewer(self.tab_view, self, self)

        self.container.layout().addWidget(action_container)
        self.container.layout().addWidget(self._file_view)

        action = QWidgetAction(self)
        action.setDefaultWidget(self.container)
        self.addAction(action)

    def createWatcher(self):
        self._watcher = FileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self.updateFileBrowser)
        self._watcher.directoryChanged.connect(self.updateTab)
        self._watcher.fileChanged.connect(self.updateFileBrowser)
        self._watcher.fileChanged.connect(self.updateTab)

    def updateFileBrowser(self):
        if os.path.exists(self._path):
            model = FileSystemModel(self._file_view)
            model.setRootPath(self._path)
            model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

            self._file_view.setModel(model)
            self._file_view.setRootIndex(model.index(self._path))
            self._file_view.hideColumn(1)
            self._file_view.hideColumn(2)
            self._file_view.hideColumn(3)

            self._watcher.changePath(os.path.abspath(self._path))

    def updateTab(self):
        for tab in self.tab_view.tabs():
            new_contents = slik.read(tab.filename())

            if tab.editor().text() != new_contents:
                tab.editor().setText(new_contents)

    def openProject(self):
        ok = QMessageBox.warning(self.parent(),
                                 'Open Project', 'Opening a project will clear '
                                                 'any unsaved changes, are you sure you want to do this?',
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                 )

        if ok == QMessageBox.StandardButton.Yes:
            path = QFileDialog.getExistingDirectory(self.parent(), 'Open Project')

            if path:
                self.setPath(path)
                self.tab_view.clear()

    def setPath(self, path: str):
        self._path = path
        self._project_dir_label.setText(f'Project Dir: {self._path}')

        self.updateFileBrowser()

    def path(self) -> str:
        return self._path

    def fileView(self) -> QTreeView:
        return self._file_view

    def animateClose(self):
        current_geometry = self.geometry()
        end_rect = QRect(
            current_geometry.center().x(),
            current_geometry.center().y(),
            1,
            1
        )

        self.close_animation = QPropertyAnimation(self, b'geometry')
        self.close_animation.setDuration(200)
        self.close_animation.setStartValue(current_geometry)
        self.close_animation.setEndValue(end_rect)
        self.close_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.close_animation.finished.connect(self.close)
        self.close_animation.start()
