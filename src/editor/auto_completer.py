from src.imports import *


class AutoCompleter(QThread):
    def __init__(self, file_name: str, api: QsciAPIs):
        super(AutoCompleter, self).__init__(None)

        self._file_name = file_name
        self._api = api

        self.line = 0
        self.index = 0
        self.text = ''

    def run(self):
        try:
            if self._file_name.endswith('.py'):
                self.loadAutoCompletions([])

            if self._file_name.endswith('.rs'):
                self.loadAutoCompletions([])

            else:
                self.loadAutoCompletions([])

        except Exception as e:
            print(e)

        self.finished.emit()

    def loadAutoCompletions(self, completions: list[str]):
        self._api.clear()

        for i in completions:
            self._api.add(i)

        self._api.prepare()

    def getCompletion(self, line: int, index: int, text: str):
        self.line = line
        self.index = index
        self.text = text.replace('\t', '    ')
        self.start()

    def setFileName(self, file_name: str):
        self._file_name = file_name

    def filename(self) -> str:
        return self._file_name