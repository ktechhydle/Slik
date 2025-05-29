import os
import slik
from PyQt6.QtCore import (Qt, QModelIndex, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve,
                          QThread, QTimer)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (QMenu, QWidgetAction, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QLineEdit, QListWidgetItem)


class FileContentsSearchIndexer(QThread):
    finished = pyqtSignal(list)

    def __init__(self, search_query: str, project_dir: str):
        super().__init__()

        self._search_query = search_query
        self._project_dir = project_dir
        self._results = {}

    def run(self):
        self._results = slik.search_file_contents(self._project_dir, self._search_query)

        self.finished.emit(self._results)

    def results(self) -> list[tuple[str, tuple[int, int]]]:
        return self._results


class FileContentsSearcher(QMenu):
    projectDirChanged = pyqtSignal(str)
    projectChanged = pyqtSignal()

    def __init__(self, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.CoverWindow)
        self.setObjectName('popup')

        self._project_dir = ''
        self.tab_view = tab_view
        self._initial_pos = None

        self.createUI()

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

        elif event.key() == Qt.Key.Key_Down and self._results_list.count() > 0:
            self._search_input.clearFocus()
            self._results_list.setFocus()
            self._results_list.setCurrentRow(0)
            self._results_list.item(0).setSelected(True)

        elif event.key() == Qt.Key.Key_Up and self._results_list.currentRow() == 0:
            self._results_list.clearSelection()
            self._results_list.clearFocus()
            self._search_input.setFocus()

        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)

        QTimer.singleShot(0, lambda: (self._search_input.setFocus(), self._search_input.selectAll()))

    def exec(self, pos=None):
        if self.isVisible():
            return

        if pos:
            super().exec(pos)
            return

        parent_center = self.parent().rect().center()
        global_center = self.parent().mapToGlobal(parent_center)
        target_width = 500
        target_height = 200

        start_rect = QRect(
            global_center.x(),
            global_center.y(),
            1,
            1
        )
        end_rect = QRect(
            global_center.x() - target_width // 2,
            global_center.y() - target_height // 2,
            target_width + 10,
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

        self._results_list.clearSelection()
        self.runSearch()
        self.show()

    def createUI(self):
        self._container = QWidget()
        self._container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._container.setLayout(QVBoxLayout())

        title_bar = QWidget()
        title_bar.setLayout(QHBoxLayout())
        title_bar.layout().setContentsMargins(0, 0, 0, 0)

        self._project_dir_label = QLabel(f"Search Contents In '{os.path.basename(self._project_dir)}'")

        close_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
        close_btn.setObjectName('actionButton')
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.animateClose)

        title_bar.layout().addWidget(self._project_dir_label)
        title_bar.layout().addStretch()
        title_bar.layout().addWidget(close_btn)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText('Search File Contents...')
        self._search_input.textChanged.connect(self.runSearch)
        self._results_list = QListWidget()
        self._results_list.itemClicked.connect(self.openFile)
        self._results_list.itemActivated.connect(self.openFile)

        self._container.layout().addWidget(title_bar)
        self._container.layout().addWidget(self._search_input)
        self._container.layout().addWidget(self._results_list)

        action = QWidgetAction(self)
        action.setDefaultWidget(self._container)
        self.addAction(action)

    def openFile(self, item: QListWidgetItem):
        if hasattr(item, 'filename'):
            self.tab_view.openTab(item.filename, cursor_pos=item.position)

        self.animateClose()

    def runSearch(self):
        if hasattr(self, '_search_indexer'):
            self._search_indexer.wait()

        self._search_indexer = FileContentsSearchIndexer(self._search_input.text(), self._project_dir)

        def search_finished(results: list[tuple[str, tuple[int, int]]]):
            print(results)
            self._results_list.clear()

            for section in results:
                filename = section[0]
                position = section[1]
                display_name = f'{os.path.relpath(filename, self._project_dir).replace('\\', '/')} - {position}'
                item = QListWidgetItem(display_name)
                item.filename = filename
                item.position = position

                self._results_list.addItem(item)

        self._search_indexer.finished.connect(search_finished)
        self._search_indexer.start()

    def setProjectDir(self, directory: str):
        if directory != self._project_dir:
            self._project_dir = directory
            self._project_dir_label.setText(f"Search Contents In '{os.path.basename(directory)}'")

            self.runSearch()

    def projectDir(self) -> str:
        return self._project_dir

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
