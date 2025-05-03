from src.imports import *
from src.gui.tab import Tab


class TabView(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index: int):
        if self.count() == 1:
            self.addTab(Tab('', self, Tab.FileTypePython, self), 'New Tab')
            self.removeTab(index - 1)

        self.removeTab(index)
        self.update()
