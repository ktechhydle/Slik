import slik
from slik import LanguageServer


class LanguageServerManager:
    def __init__(self, tab_view):
        self._tab_view = tab_view
        self._tab_view.tabOpened.connect(self.openDocument)
        self._tab_view.tabClosed.connect(self.closeDocument)

        self._language_server = LanguageServer()

    def openDocument(self, filename: str):
        self._language_server.open_document(filename)

    def closeDocument(self, filename: str):
        self._language_server.close_document(filename)
