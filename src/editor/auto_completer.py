from src.imports import *


class AutoCompleter(QThread):
    def __init__(self, file_name: str, api: QsciAPIs):
        super(AutoCompleter, self).__init__(None)

        self._file_name = file_name
        self._api = api

        self.line = 0
        self.column = 0
        self.text = ''

    def run(self):
        try:
            self.loadAutoCompletions(slik.get_completions(self._file_name, self.text, self.line, self.column))

        except Exception as e:
            raise e

        self.finished.emit()

    def loadAutoCompletions(self, completions: list[str]):
        self._api.clear()

        for i in completions:
            self._api.add(i)

        self._api.prepare()

    def getCompletion(self, line: int, column: int, text: str):
        self.line = line
        self.column = column
        self.text = text.replace('\t', '    ')
        self.start()

    def setFileName(self, file_name: str):
        self._file_name = file_name

    def filename(self) -> str:
        return self._file_name