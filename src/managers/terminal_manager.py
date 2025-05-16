import os


class TerminalManager:
    def __init__(self):
        self._project_dir = ''

    def newTerminal(self):
        os.system(f'start cmd.exe /k "cd /d {self._project_dir}"')

    def terminalFromCommand(self, command: str):
        os.system(f'start cmd.exe /k "cd /d {self._project_dir} && {command}"')

    def setProjectDir(self, directory: str):
        if directory != self._project_dir:
            self._project_dir = directory

    def projectDir(self) -> str:
        return self._project_dir
