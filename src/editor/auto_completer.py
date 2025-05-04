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
                self.loadAutoCompletions(jedi.Script(self.text, path=self._file_name).complete(self.line, self.index))

            if self._file_name.endswith('.rs'):
                self.loadAutoCompletions(slik.get_completions(self.text, self.line, self.index))

            else:
                self.loadAutoCompletions([])

        except Exception as e:
            print(e)

        self.finished.emit()

    def loadAutoCompletions(self, completions: list[jedi.api.Completion | str]):
        self._api.clear()

        for i in completions:
            if isinstance(i, str):
                self._api.add(i)

            else:
                self._api.add(i.complete)

        self._api.prepare()

    def getCompletion(self, line: int, index: int, text: str):
        self.line = line
        self.index = index
        self.text = text.replace('\t', '    ')
        self.start()