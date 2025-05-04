from src.imports import *
from src.gui.tab import Tab


class FileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)

            if file_path.endswith('.py'):
                return QIcon('resources/icons/python_icon.svg')

            if file_path.endswith('.rs'):
                return QIcon('resources/icons/rust_icon.svg')

        return super().data(index, role)


class FileSystemWatcher(QFileSystemWatcher):
    def __init__(self, parent=None):
        super().__init__(parent)

    def changePath(self, path: str):
        self.clear()
        self.addPath(path)

    def clear(self):
        self.removePaths(self.directories())


class FileBrowser(QMenu):
    def __init__(self, path: str, tab_view, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Popup)
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

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

        super().exec(end_rect.topLeft())

    def createUI(self):
        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())

        action_container = QWidget()
        action_container.setLayout(QHBoxLayout())
        action_container.layout().setContentsMargins(0, 0, 0, 0)

        open_project_btn = QPushButton('📁', self)
        open_project_btn.setObjectName('actionButton')
        open_project_btn.setFixedSize(25, 25)
        open_project_btn.clicked.connect(self.openProject)
        rename_file_btn = QPushButton('✏️', self)
        rename_file_btn.setObjectName('actionButton')
        rename_file_btn.setFixedSize(25, 25)
        self._project_dir_label = QLabel('')

        action_container.layout().addWidget(open_project_btn)
        action_container.layout().addWidget(rename_file_btn)
        action_container.layout().addStretch()
        action_container.layout().addWidget(self._project_dir_label)

        self._file_view = QTreeView(self)
        self._file_view.setAnimated(True)
        self._file_view.setHeaderHidden(True)
        self._file_view.doubleClicked.connect(self.openFile)

        self.container.layout().addWidget(action_container)
        self.container.layout().addWidget(self._file_view)

        action = QWidgetAction(self)
        action.setDefaultWidget(self.container)
        self.addAction(action)

    def createWatcher(self):
        self._watcher = FileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self.updateFileBrowser)
        self._watcher.fileChanged.connect(self.updateFileBrowser)

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

    def openFile(self, index: QModelIndex):
        model = self._file_view.model()
        filepath = model.filePath(index)

        if not model.isDir(index):
            if filepath.endswith('.py'):
                self.tab_view.addTab(Tab(filepath, self.tab_view, Tab.FileTypePython, self.tab_view), insert=True)

            else:
                self.tab_view.addTab(Tab(filepath, self.tab_view, Tab.FileTypePlainText, self.tab_view), insert=True)

    def openProject(self):
        path = QFileDialog.getExistingDirectory(self.parent(), 'Open Project')

        if path:
            self.setPath(path)
            self.tab_view.clear()

        self.exec()

    def setPath(self, path: str):
        self._path = path
        self._project_dir_label.setText(f'Project Dir: {os.path.abspath(self._path)}')

        self.updateFileBrowser()

    def path(self) -> str:
        return self._path

    def fileView(self) -> QTreeView:
        return self._file_view
