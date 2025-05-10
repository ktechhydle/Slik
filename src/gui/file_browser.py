from src.imports import *
from src.gui.tab import Tab
from src.gui.title_bar import TitleBar
from src.gui.message_dialog import MessageDialog


class FileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)

            def make_icon(path):
                pixmap = QPixmap(path)
                icon = QIcon()
                icon.addPixmap(pixmap, QIcon.Mode.Normal)
                icon.addPixmap(pixmap, QIcon.Mode.Selected)

                return icon

            if file_path.endswith('.py'):
                return make_icon('resources/icons/logos/python_icon.svg')

            elif file_path.endswith('.rs'):
                return make_icon('resources/icons/logos/rust_icon.svg')

            elif os.path.isdir(file_path):
                return make_icon('resources/icons/ui/folder_icon.svg')

            else:
                return make_icon('resources/icons/ui/txt_icon.svg')

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

        message = MessageDialog('Remove',
                                f'Are you sure you want to delete the {len(paths)} selected items?',
                                (MessageDialog.YesButton, MessageDialog.NoButton),
                                self.tab_view)
        message.exec()

        if message.result() == MessageDialog.Accepted:
            for path in paths:
                try:
                    if os.path.isfile(path):
                        os.remove(path)

                    elif os.path.isdir(path):
                        shutil.rmtree(path)

                except Exception as e:
                    raise e


class FileBrowser(QMenu):
    projectDirChanged = pyqtSignal(str)
    projectChanged = pyqtSignal()

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
        if self.isVisible():
            return

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
        self._container.setFixedSize(target_width - 5, target_height - 5)
        self.updateFileBrowser()

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

        self.show()

    def createUI(self):
        self._container = QWidget()
        self._container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._container.setLayout(QVBoxLayout())

        self._title_bar = TitleBar(self, create=False)

        self._project_dir_label = QLabel('')
        open_project_btn = QPushButton(QIcon('resources/icons/ui/folder_icon.svg'), '', self)
        open_project_btn.setObjectName('actionButton')
        open_project_btn.setFixedSize(25, 25)
        open_project_btn.clicked.connect(self.openProject)
        close_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
        close_btn.setObjectName('actionButton')
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.animateClose)

        self._title_bar.layout().addWidget(self._project_dir_label)
        self._title_bar.layout().addStretch()
        self._title_bar.layout().addWidget(open_project_btn)
        self._title_bar.layout().addWidget(close_btn)

        self._file_view = FileSystemViewer(self.tab_view, self, self)

        self._container.layout().addWidget(self._title_bar)
        self._container.layout().addWidget(self._file_view)

        action = QWidgetAction(self)
        action.setDefaultWidget(self._container)
        self.addAction(action)

    def createWatcher(self):
        self._watcher = FileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self.projectChanged.emit)
        self._watcher.directoryChanged.connect(self.updateFileBrowser)
        self._watcher.fileChanged.connect(self.projectChanged.emit)
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

    def openProject(self):
        message = MessageDialog('Open Project', 'Opening a project will clear '
                                                 'any unsaved changes, are you sure you want to do this?',
                                (MessageDialog.YesButton, MessageDialog.NoButton),
                                self)
        message.exec()

        if message.result() == MessageDialog.Accepted:
            path = QFileDialog.getExistingDirectory(self.parent(), 'Open Project')

            if path:
                self.setPath(path)
                self.tab_view.clear()

    def setPath(self, path: str):
        self._path = path
        self._project_dir_label.setText(f'Project Dir: {self._path}')

        self.projectDirChanged.emit(self._path)
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
