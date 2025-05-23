import slik
from slik import LanguageServer
from PyQt6.Qsci import QsciAPIs, QsciScintilla
from PyQt6.QtCore import Qt


class LanguageServerManager:
    def __init__(self, tab_view):
        self._tab_view = tab_view
        self._tab_view.tabOpened.connect(self.openDocument)
        self._tab_view.tabClosed.connect(self.closeDocument)
        self._tab_view.tabCompletionRequested.connect(self.getDocumentCompletions)
        self._tab_view.tabHotSpotRequested.connect(self.getDocumentDeclarationsAndUsages)

        self._language_server = LanguageServer()

    def openDocument(self, filename: str):
        self._language_server.open_document(filename)

    def closeDocument(self, filename: str):
        self._language_server.close_document(filename)

    def getDocumentCompletions(self, editor: QsciScintilla, api: QsciAPIs):
        if not editor.selectedText():
            line, column = editor.getCursorPosition()
            completions = ['greet(name: str)'] # self._language_server.get_document_completions()

            api.clear()

            for i in completions:
                api.add(i)

            api.prepare()
            editor.autoCompleteFromAPIs()

    def getDocumentDeclarationsAndUsages(self, editor: QsciScintilla, position: int, modifiers: Qt.KeyboardModifier):
        line, column = editor.lineIndexFromPosition(position)

        if modifiers and Qt.KeyboardModifier.ControlModifier:
            print(f'Declaration requested here: {line}:{column}')

        elif modifiers and Qt.KeyboardModifier.AltModifier:
            print(f'Usages requested here: {line}:{column}')
