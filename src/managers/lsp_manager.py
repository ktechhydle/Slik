import slik


class LanguageServerManager:
    def __init__(self, tab_view):
        self._tab_view = tab_view
        self._tab_view.tabOpened.connect(self.openDocument)
        self._tab_view.tabClosed.connect(self.closeDocument)

    def openDocument(self, filename: str):
        slik.open_document(filename)

    def closeDocument(self, filename: str):
        slik.close_document(filename)
