from src.imports import *
from mp_software_stylesheets.styles import SLIKCSS
from src.gui.tab import Tab
from src.gui.tab_view import TabView


class Slik(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Slik')
        self.setWindowIcon(QIcon('resources/icons/slik_icon.svg'))
        self.resize(1000, 800)

        self.createUI()

    def createUI(self):
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)

        self.tab_view = TabView()
        self.tab_view.addTab(Tab('', self.tab_view, Tab.FileTypeRust, self), 'test.py')

        container.layout().addWidget(self.tab_view)
        self.setCentralWidget(container)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(SLIKCSS)

    QFontDatabase.addApplicationFont('resources/fonts/JetBrainsMono-Regular.ttf')

    window = Slik()
    window.show()

    # Crash handler
    def handle_exception(exctype, value, tb):
        QMessageBox.critical(window, 'Error:(', f'Ibrowse encountered an error:\n\n{value}\n')
        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    sys.exit(app.exec())

if __name__ == '__main__':
    main()