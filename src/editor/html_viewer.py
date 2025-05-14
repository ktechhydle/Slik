import json
import markdown
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class HtmlViewer(QWebEngineView):
    def __init__(self, project_dir='', parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self._project_dir = project_dir

    def setHtml(self, html, baseUrl=None):
        if baseUrl:
            super().setHtml(html, baseUrl)

            return

        super().setHtml(html, QUrl.fromLocalFile(self._project_dir + '/'))

    def setMarkdown(self, md: str):
        # convert md to html
        html_body = markdown.markdown(md)

        self.page().runJavaScript(f"updateContent({json.dumps(html_body)});")

    def setProjectDir(self, directory: str):
        self._project_dir = directory

    def projectDir(self) -> str:
        return self._project_dir