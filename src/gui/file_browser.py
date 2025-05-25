import os
import shutil
import slik
from PyQt6.QtCore import (QMimeData, Qt, QFileSystemWatcher, QModelIndex, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve,
    QDir, QUrl)
from PyQt6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QFileSystemModel, QPixmap, QIcon, QAction, QDesktopServices, QKeySequence
from PyQt6.QtWidgets import (QTreeView, QMenu, QInputDialog, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLabel,
    QPushButton, QWidgetAction, QFileDialog, QApplication)
from src.gui.message_dialog import MessageDialog
from src.gui.input_dialog import InputDialog
from src.gui.move_dialog import MoveDialog


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

            elif file_path.endswith('.html'):
                return make_icon('resources/icons/logos/html_icon.svg')

            elif file_path.endswith('.css'):
                return make_icon('resources/icons/logos/css_icon.svg')

            elif file_path.endswith('.md'):
                return make_icon('resources/icons/logos/markdown_icon.svg')

            elif file_path.endswith('.svg'):
                return make_icon('resources/icons/logos/svg_icon.svg')

            elif file_path.endswith(('LICENSE', 'LICENSE.txt')):
                return make_icon('resources/icons/logos/license_icon.svg')

            elif file_path.endswith(('.toml', '.lock')):
                return make_icon('resources/icons/logos/toml_icon.svg')

            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff')):
                return make_icon('resources/icons/logos/image_icon.svg')

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
        if self.directories():
            self.removePaths(self.directories())


class FileSystemViewer(QTreeView):
    def __init__(self, tab_view, file_browser, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setIndentation(15)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tab_view = tab_view
        self.file_browser = file_browser

        self.customContextMenuRequested.connect(self.showMenu)
        self.doubleClicked.connect(self.openFile)

        self.createActions()

    def showMenu(self, pos):
        if not hasattr(self, 'menu'):
            self.menu = QMenu(self.tab_view)

            new_file_action = QAction('New File', self)
            new_file_action.triggered.connect(self.newFile)

            new_dir_action = QAction('New Directory', self)
            new_dir_action.triggered.connect(self.newDir)

            rename_action = QAction('Rename...', self)
            rename_action.triggered.connect(self.renameSelected)

            move_action = QAction('Move...', self)
            move_action.triggered.connect(self.moveSelected)

            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(self.removeSelected)

            copy_file_action = QAction('Copy File', self)
            copy_file_action.triggered.connect(self.copyFile)

            copy_full_path_action = QAction('Copy Full Path', self)
            copy_full_path_action.triggered.connect(self.copyPath)

            copy_relative_path_action = QAction('Copy Relative Path', self)
            copy_relative_path_action.triggered.connect(lambda: self.copyPath(relative=True))

            paste_file_action = QAction('Paste File', self)
            paste_file_action.triggered.connect(self.pasteFile)

            open_in_explorer_action = QAction('Open In Explorer', self)
            open_in_explorer_action.triggered.connect(self.openExplorer)

            open_in_application_action = QAction('Open In Associated App', self)
            open_in_application_action.triggered.connect(self.openAssociated)

            self.menu.addAction(new_file_action)
            self.menu.addAction(new_dir_action)
            self.menu.addSeparator()
            self.menu.addAction(rename_action)
            self.menu.addAction(move_action)
            self.menu.addSeparator()
            self.menu.addAction(delete_action)
            self.menu.addSeparator()
            self.menu.addAction(copy_file_action)
            self.menu.addAction(copy_full_path_action)
            self.menu.addAction(copy_relative_path_action)
            self.menu.addSeparator()
            self.menu.addAction(paste_file_action)
            self.menu.addSeparator()
            self.menu.addAction(open_in_explorer_action)
            self.menu.addAction(open_in_application_action)

        self.menu.exec(self.mapToGlobal(pos))

    def createActions(self):
        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence('Ctrl+C'))
        copy_action.triggered.connect(self.copyFile)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence('Ctrl+V'))
        paste_action.triggered.connect(self.pasteFile)

        delete_action = QAction('Delete', self)
        delete_action.setShortcut(QKeySequence('Backspace'))
        delete_action.triggered.connect(self.removeSelected)

        self.addAction(copy_action)
        self.addAction(paste_action)
        self.addAction(delete_action)

    def newFile(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            filepath = self.model().filePath(index)
            dir_path = os.path.dirname(filepath) if os.path.isfile(filepath) else filepath

            input_dialog = InputDialog('New File', 'Name:', (InputDialog.OkButton, InputDialog.CancelButton), self.tab_view)
            input_dialog.exec()

            if input_dialog.result() == InputDialog.Accepted:
                filename = os.path.join(dir_path, input_dialog.value())

                if os.path.exists(os.path.abspath(filename)):
                    message = MessageDialog('Overwrite Error', f"A file with the name '{os.path.basename(filename)}' already exists.", (InputDialog.OkButton,), self.tab_view)
                    message.exec()

                    return

                slik.write(os.path.abspath(filename), '')

    def newDir(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            filepath = self.model().filePath(index)
            dir_path = os.path.dirname(filepath) if os.path.isfile(filepath) else filepath

            input_dialog = InputDialog('New Directory', 'Name:', (InputDialog.OkButton, InputDialog.CancelButton), self.tab_view)
            input_dialog.exec()

            if input_dialog.result() == InputDialog.Accepted:
                filename = os.path.join(dir_path, input_dialog.value())

                if os.path.exists(os.path.abspath(filename)):
                    message = MessageDialog('Overwrite Error',
                                            f"A directory with the name '{os.path.basename(filename)}' already exists.",
                                            (InputDialog.OkButton,), self.tab_view)
                    message.exec()

                    return

                os.mkdir(os.path.abspath(filename))

    def openFile(self, index: QModelIndex):
        model = self.model()
        filepath = model.filePath(index)

        if not model.isDir(index):
            self.tab_view.openTab(filepath, insert=True)

    def openExplorer(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            filepath = self.model().filePath(index)

            if self.model().isDir(index):
                QDesktopServices.openUrl(QUrl(filepath))

            else:
                QDesktopServices.openUrl(QUrl(os.path.dirname(filepath)))

    def openAssociated(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            filepath = self.model().filePath(index)
            QDesktopServices.openUrl(QUrl(filepath))

    def renameSelected(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            model = self.model()
            old_path = model.filePath(index)
            old_name = os.path.basename(old_path)
            dir_path = os.path.dirname(old_path)

            input_dialog = InputDialog(f"Rename '{old_name}'", 'New filename:', (InputDialog.OkButton, InputDialog.NoButton), self.tab_view)
            input_dialog.exec()

            if input_dialog.result() == InputDialog.Accepted:
                new_path = os.path.join(dir_path, input_dialog.value())

                if new_path != old_path:
                    try:
                        os.rename(old_path, new_path)

                    except Exception as e:
                        raise e

    def moveSelected(self):
        indexes = self.selectedIndexes()

        if not indexes:
            return

        model = self.model()
        paths = list(set(model.filePath(index) for index in indexes if index.isValid()))

        move_dialog = MoveDialog('Move', 'Choose a destination path:',
                                 (MoveDialog.OkButton, MoveDialog.CancelButton), self)
        move_dialog.input().setText(os.path.dirname(paths[0].replace('\\', '/')) + '/')
        move_dialog.exec()

        if move_dialog.result() == MoveDialog.Accepted:
            dest_dir = move_dialog.value()

            if not os.path.exists(dest_dir):
                message = MessageDialog('Invalid Destination',
                                        f"The path '{dest_dir}' does not exist.",
                                        (MessageDialog.OkButton,), self.tab_view)
                message.exec()

                return

            confirm = MessageDialog('Confirm Move',
                                    f'Move {len(paths)} item(s) to:\n{dest_dir}?',
                                    (MessageDialog.YesButton, MessageDialog.NoButton),
                                    self.tab_view)
            confirm.exec()

            if confirm.result() == MessageDialog.Accepted:
                for path in paths:
                    try:
                        filename = os.path.basename(path)
                        target_path = os.path.join(dest_dir, filename)

                        if os.path.exists(target_path):
                            overwrite = MessageDialog('Overwrite?',
                                                      f"'{filename}' already exists at destination. Overwrite?",
                                                      (MessageDialog.YesButton, MessageDialog.NoButton),
                                                      self.tab_view)
                            overwrite.exec()

                            if overwrite.result() != MessageDialog.Accepted:
                                continue

                            if os.path.isdir(target_path):
                                shutil.rmtree(target_path)

                            else:
                                os.remove(target_path)

                        shutil.move(path, target_path)

                    except Exception as e:
                        error = MessageDialog('Move Error',
                                              f"Could not move '{os.path.basename(path)}': {str(e)}",
                                              (MessageDialog.OkButton,), self.tab_view)
                        error.exec()

    def removeSelected(self):
        if self.selectedIndexes():
            indexes = self.selectedIndexes()
            model = self.model()
            paths = list(set(model.filePath(index) for index in indexes))

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

    def copyFile(self):
        indexes = self.selectedIndexes()

        if not indexes:
            return

        model = self.model()
        urls = []

        for index in indexes:
            if not index.isValid():
                continue

            filepath = model.filePath(index)
            urls.append(QUrl.fromLocalFile(filepath))

        mime_data = QMimeData()
        mime_data.setUrls(urls)  # Set file urls on clipboard

        QApplication.clipboard().setMimeData(mime_data)

    def copyPath(self, relative=False):
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]

            if not index.isValid():
                return

            filepath = self.model().filePath(index)

            if relative:
                QApplication.clipboard().setText(os.path.relpath(self.file_browser.projectDir(), filepath).replace('\\', '/'))

            else:
                QApplication.clipboard().setText(os.path.abspath(filepath).replace('\\', '/'))

    def pasteFile(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not mime_data or not mime_data.hasUrls():
            return

        urls = mime_data.urls()

        if not urls:
            return

        if self.selectedIndexes():
            index = self.selectedIndexes()[0]
            dest_dir = self.model().filePath(index)

            if os.path.isfile(dest_dir):
                dest_dir = os.path.dirname(dest_dir)

        else:
            dest_dir = self.file_browser.projectDir()  # fallback

        for url in urls:
            src_path = url.toLocalFile()
            basename = os.path.basename(src_path)
            target_path = os.path.join(dest_dir, basename)

            if os.path.exists(target_path):
                overwrite = MessageDialog('Overwrite',
                                          f"'{basename}' already exists. Overwrite?",
                                          (MessageDialog.YesButton, MessageDialog.NoButton),
                                          self.tab_view)
                overwrite.exec()

                if overwrite.result() != MessageDialog.Accepted:
                    continue

                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)

                else:
                    os.remove(target_path)

            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, target_path)

                else:
                    shutil.copy2(src_path, target_path)

            except Exception as e:
                error = MessageDialog('Paste Error',
                                      f"Could not paste '{basename}': {str(e)}",
                                      (MessageDialog.OkButton,), self.tab_view)
                error.exec()


class FileBrowser(QMenu):
    projectDirChanged = pyqtSignal(str)
    projectChanged = pyqtSignal()

    def __init__(self, path: str, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.CoverWindow)
        self.setObjectName('fileBrowser')

        self._path = path
        self.tab_view = tab_view
        self._initial_pos = None

        self.createUI()
        self.createWatcher()
        self.updateFileBrowser()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._initial_pos = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._initial_pos is not None:
            delta = event.position().toPoint() - self._initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        self._initial_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.animateClose()

        else:
            super().keyPressEvent(event)

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

        title_bar = QWidget()
        title_bar.setLayout(QHBoxLayout())
        title_bar.layout().setContentsMargins(0, 0, 0, 0)

        self._project_dir_label = QLabel('')
        open_project_btn = QPushButton(QIcon('resources/icons/ui/folder_icon.svg'), '', self)
        open_project_btn.setObjectName('actionButton')
        open_project_btn.setFixedSize(25, 25)
        open_project_btn.clicked.connect(self.openProject)
        close_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
        close_btn.setObjectName('actionButton')
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.animateClose)

        title_bar.layout().addWidget(self._project_dir_label)
        title_bar.layout().addStretch()
        title_bar.layout().addWidget(open_project_btn)
        title_bar.layout().addWidget(close_btn)

        self._file_view = FileSystemViewer(self.tab_view, self, self)

        self._container.layout().addWidget(title_bar)
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

            scroll_pos_x = self._file_view.verticalScrollBar().value()
            scroll_pos_y = self._file_view.horizontalScrollBar().value()
            self._file_view.setModel(model)
            self._file_view.setRootIndex(model.index(self._path))
            self._file_view.hideColumn(1)
            self._file_view.hideColumn(2)
            self._file_view.hideColumn(3)
            self._file_view.horizontalScrollBar().setValue(scroll_pos_x)
            self._file_view.verticalScrollBar().setValue(scroll_pos_y)

            self._watcher.changePath(self._path)

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
