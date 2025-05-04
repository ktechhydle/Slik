from src.imports import *


class MarkdownViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def setMarkdown(self, md: str):
        # Convert Markdown to HTML
        html_body = markdown.markdown(md)

        # Define your CSS styles
        css = '''
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    color: #333;
                    background-color: #1e1e1e;
                }
                
                h1, h2, h3, h4, h5, p, li {
                    color: #ffffff;
                }
                
                a {
                    color: #6b9bfa;
                    font-weight: bold;
                    text-decoration: none;
                }
                
                a:hover {
                    text-decoration: underline;
                }
                
                code {
                    background-color: #535353;
                    padding: 2px 4px;
                    border-radius: 4px;
                    font-family: monospace;
                }
                
                pre {
                    background-color: #f4f4f4;
                    padding: 10px;
                    overflow-x: auto;
                    border-radius: 4px;
                }
                
                blockquote {
                    margin: 10px 0;
                    padding-left: 10px;
                    border-left: 3px solid #ccc;
                    color: #666;
                }
            </style>
        '''

        # Combine CSS and HTML into a full HTML document
        html = f'<!DOCTYPE html><html><head>{css}</head><body>{html_body}</body></html>'

        self.setHtml(html)