from src.imports import Qt, QWidget, QLabel, QPushButton, QIcon, QHBoxLayout


class TitleBar(QWidget):
    def __init__(self, parent, create=True):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        if create:
            self.createUI()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.parent().window().move(
                self.parent().window().x() + delta.x(),
                self.parent().window().y() + delta.y(),
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.initial_pos = None

        super().mouseReleaseEvent(event)

    def createUI(self):
        self._title_label = QLabel(self.parent().title())

        close_btn = QPushButton(QIcon('resources/icons/ui/close_icon.svg'), '', self)
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.parent().animateClose)

        self.layout().addWidget(self._title_label)
        self.layout().addStretch()
        self.layout().addWidget(close_btn)

    def setTitle(self, title: str):
        self._title_label.setText(title)

    def title(self) -> str:
        return self._title_label.text()