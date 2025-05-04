from src.imports import *


class MarkdownViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setMarkdown(self, md: str):
        md = markdown.markdown(md)

        self.setHtml(md)