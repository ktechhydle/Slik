use pyo3::prelude::*;
use serde::{self, Deserialize, Serialize};
use serde_json::json;

const JSON_RPC_VERSION: &str = "2.0";

#[derive(Serialize, Deserialize)]
enum RequestID {
    Completion(i32),
    Definition(i32),
    Usage(i32),
    Document(i32),
}

#[pyclass]
pub struct LanguageServer;

#[pymethods]
impl LanguageServer {
    // Basic language server communication built in rust, wrapped to python
    // Request IDs:
    // 1 - Completions
    // 2 - Definitions
    // 3 - Usages
    // 4 - Document Opened
    // 5 - Document Closed
    #[new]
    fn new() -> Self {
        LanguageServer {}
    }

    // Start the lsp command for the document (pyright for .py, rust-analyzer for .rs)
    // This will send a 'textDocument/didOpen' request to the server
    pub fn open_document(&self, filename: &str) -> PyResult<()> {
        /*let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": RequestID::Document(4),
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": format!("file://{}", filename)
                }
            }
        });*/

        Ok(())
    }

    // Stop the lsp command for the specified file
    // This will send a 'textDocument/didClose' request to the server
    pub fn close_document(&self, filename: &str) -> PyResult<()> {
        /*let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": RequestID::Document(5),
            "method": "textDocument/didClose",
            "params": {
                "textDocument": {
                    "uri": format!("file://{}", filename)
                }
            }
        });*/

        Ok(())
    }

    // Get code completitions for the document
    // This will send a 'textDocument/completion' request to the server
    pub fn get_document_completions(
        &self,
        filename: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<Vec<String>> {
        /*let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": RequestID::Completion(1),
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": format!("file://{}", filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });*/

        Ok(vec!["".to_string()])
    }

    // Get definitions for the document (based on position)
    // This will send a 'textDocument/definition' request to the server
    pub fn get_document_definitions(
        &self,
        filename: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        /*let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": RequestID::Definition(2),
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": format!("file://{}", filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });*/

        Ok(())
    }

    // Get usages for the document (based on position)
    // This will send a 'textDocument/references' request to the server
    pub fn get_document_usages(
        &self,
        filename: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        /*let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": RequestID::Usage(3),
            "method": "textDocument/references",
            "params": {
                "textDocument": {
                    "uri": format!("file://{}", filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });*/

        Ok(())
    }
}
