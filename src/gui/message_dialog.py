from PyQt6.QtCore import Qt, QSize, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QMenu, QApplication, QVBoxLayout, QWidget, QLabel, QWidgetAction
from src.gui.title_bar import TitleBar


class MessageDialog(QMenu):
    OkButton = ('Ok', 0)
    CancelButton = ('Cancel', 1)
    YesButton = ('Yes', 0)
    NoButton = ('No', 1)
    Accepted = 0
    Rejected = 1

    def __init__(self, title: str, message: str, standard_buttons: tuple, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags()
                            | Qt.WindowType.CoverWindow
                            | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.NoDropShadowWindowHint
                            | Qt.WindowType.WindowType_Mask)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName('popup')

        self._title = title
        self._message = message
        self._standard_btns = standard_buttons
        self._target_size = QSize(400, 200)
        self._result = None

        self.createUI()
        self.createButtons()

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
        target_width, target_height = self._target_size.width(), self._target_size.height()

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
        self._container.setFixedSize(target_width - 5, target_height - 5) # we need to add a small padding

        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(250)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

        QApplication.beep()
        super().exec()

    def createUI(self):
        self._container = QWidget()
        self._container.setLayout(QVBoxLayout())

        self._title_bar = TitleBar(self)
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(True)

        self._container.layout().addWidget(self._title_bar)
        self._container.layout().addSpacing(20)
        self._container.layout().addWidget(self._message_label)
        self._container.layout().addStretch()

        action = QWidgetAction(self)
        action.setDefaultWidget(self._container)
        self.addAction(action)

    def createButtons(self):
        button_box = QWidget()
        button_box.setLayout(QHBoxLayout())
        button_box.layout().setContentsMargins(0, 0, 0, 0)
        button_box.layout().addStretch()

        for name, value in self._standard_btns:
            button = QPushButton(name, self)
            button.setFixedWidth(100)
            button.setProperty('default', False)

            if value == 0:
                button.setProperty('default', True) # make the button underlined
                button.clicked.connect(self.accept)

            else:
                button.clicked.connect(self.reject)

            button_box.layout().addWidget(button)

        self._container.layout().addWidget(button_box)
        self._container.layout().addSpacing(10)

    def accept(self):
        self._result = 0
        self.animateClose()

    def reject(self):
        self._result = 1
        self.animateClose()

    def setTitle(self, title: str):
        self._title = title
        self._title_bar.setTitle(self._title)

    def setStandardButtons(self, buttons: tuple):
        self._standard_btns = buttons

    def setTargetSize(self, size: QSize):
        self._target_size = size

    def titleBar(self) -> TitleBar:
        return self._title_bar

    def title(self) -> str:
        return self._title

    def standardButtons(self) -> tuple:
        return self._standard_btns

    def targetSize(self) -> QSize:
        return self._target_size

    def result(self) -> int:
        return self._result

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
