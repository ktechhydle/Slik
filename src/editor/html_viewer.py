import json
import markdown
import webbrowser
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class HtmlPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            webbrowser.open(url.url())

            return False

        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class HtmlViewer(QWebEngineView):
    def __init__(self, project_dir='', parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setPage(HtmlPage(self))

        self._project_dir = project_dir
        self._pending_content = None

        self.loadFinished.connect(self.loadingFinished)

    def setHtml(self, html, baseUrl=None):
        if baseUrl:
            super().setHtml(html, baseUrl)

            return

        super().setHtml(html, QUrl.fromLocalFile(self._project_dir + '/'))

    def setSvg(self, svg: str):
        self._pending_content = json.dumps(svg)
        self.updateContent()

    def setMarkdown(self, md: str):
        # convert md to html
        html_body = markdown.markdown(md, extensions=['fenced_code', 'tables'])

        self._pending_content = json.dumps(html_body)
        self.updateContent()

    def loadingFinished(self, ok: bool):
        if ok and self._pending_content:
            js = f'updateContent({self._pending_content});'
            self.page().runJavaScript(js)

            self._pending_content = None

    def updateContent(self):
        self.page().runJavaScript(f'updateContent({self._pending_content});')

    def setProjectDir(self, directory: str):
        self._project_dir = directory

    def projectDir(self) -> str:
        return self._project_dir
