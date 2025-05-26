use pyo3::prelude::*;
use serde_json::json;
use std::{
    collections::HashMap,
    io::BufReader,
    process::{Child, ChildStdin, ChildStdout, Command, Stdio},
};

const JSON_RPC_VERSION: &str = "2.0";

fn as_uri(filename: &str) -> String {
    let result = format!("file://{}", filename);

    result.to_string()
}

#[pyclass]
pub struct LanguageServer {
    rust_lsp_command: &'static str,
    python_lsp_command: &'static str,
}

#[pymethods]
impl LanguageServer {
    // Basic language server communication built in rust, wrapped to python
    // Starts both a rust-analyzer and pyright-langserver command to communicate with depending on the language
    // This will essentially send one request, then retrieve results. No async, no threading, one request at a time.
    #[new]
    fn new() -> Self {
        // let python_command = Command::new("node_modules/.bin/pyright-langserver.cmd")
        //     .arg("--stdio")
        //     .stdin(Stdio::piped())
        //     .stdout(Stdio::piped())
        //     .spawn();

        // let python_writer = python_command.unwrap().stdin.take().unwrap();
        // let python_reader = BufReader::new(python_command.unwrap().stdout.take().unwrap());

        LanguageServer {
            rust_lsp_command: "rust-analyzer",
            python_lsp_command: "node_modules/.bin/pyright-langserver.cmd",
        }
    }

    // Start the lsp command for the document (pyright for .py, rust-analyzer for .rs)
    // This will send a 'textDocument/didOpen' request to the server
    pub fn open_document(&self, filename: &str) -> PyResult<()> {
        let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": 1,
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": as_uri(filename)
                }
            }
        });

        Ok(())
    }

    // Stop the language server commands for the specified file
    // This will send a 'textDocument/didClose' request to the server
    pub fn close_document(&self, filename: &str) -> PyResult<()> {
        let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": 1,
            "method": "textDocument/didClose",
            "params": {
                "textDocument": {
                    "uri": as_uri(filename)
                }
            }
        });

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
        let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": 1,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": as_uri(filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });

        Ok(vec!["".to_string()])
    }

    // Get definitions for the document (based on position)
    // This will send a 'textDocument/definition' request to the server
    // Returns HashMap(filename, (line, column))
    pub fn get_document_definitions(
        &self,
        filename: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<HashMap<String, (usize, usize)>> {
        let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": 1,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": as_uri(filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });

        let mut results = HashMap::new();
        results.insert("example.txt".to_string(), (line, column));

        Ok(results)
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
        let request = json!({
            "jsonrpc": JSON_RPC_VERSION,
            "id": 1,
            "method": "textDocument/references",
            "params": {
                "textDocument": {
                    "uri": as_uri(filename)
                },
                "position": {
                    "line": line,
                    "character": column
                }
            }
        });

        Ok(())
    }
}
