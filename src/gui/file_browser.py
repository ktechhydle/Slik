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


class FileBrowser(QMenu):
    def __init__(self, path: str, tab_view, parent=None):
        super().__init__(parent)
        self.setObjectName('blankWidget')

        self._path = path
        self.tab_view = tab_view

        self.createUI()
        self.updateView()

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

        self.file_view = QTreeView(self)
        self.file_view.setAnimated(True)
        self.file_view.setHeaderHidden(True)
        self.file_view.doubleClicked.connect(self.openFile)

        self.container.layout().addWidget(self.file_view)

        action = QWidgetAction(self)
        action.setDefaultWidget(self.container)
        self.addAction(action)

    def updateView(self):
        if os.path.exists(self._path):
            model = FileSystemModel(self.file_view)
            model.setRootPath(self._path)
            model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

            self.file_view.setModel(model)
            self.file_view.setRootIndex(model.index(self._path))
            self.file_view.hideColumn(1)
            self.file_view.hideColumn(2)
            self.file_view.hideColumn(3)

    def openFile(self, index: QModelIndex):
        model = self.file_view.model()
        filepath = model.filePath(index)

        if not model.isDir(index):
            if filepath.endswith('.py'):
                self.tab_view.addTab(Tab(filepath, self.tab_view, Tab.FileTypePython, self.tab_view))


    def setPath(self, path: str):
        self._path = path

        self.updateView()

    def path(self) -> str:
        return self._path
