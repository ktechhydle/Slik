use lsp_types;
use pyo3::prelude::*;

#[pyclass]
pub struct LanguageServer;

#[pymethods]
impl LanguageServer {
    #[new]
    fn new() -> Self {
        LanguageServer {}
    }

    pub fn start(&self) {}

    pub fn open_document(&self, file: &str) -> PyResult<()> {
        Ok(())
    }

    pub fn close_document(&self, file: &str) -> PyResult<()> {
        Ok(())
    }

    pub fn get_document_completions(
        &self,
        file: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<Vec<String>> {
        Ok(vec!["greet(name: str)".to_string()])
    }

    pub fn get_document_definitions(
        &self,
        file: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        Ok(())
    }

    pub fn get_document_usages(
        &self,
        file: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        Ok(())
    }

    pub fn format_document(
        &self,
        file: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        Ok(())
    }

    pub fn lint_document(
        &self,
        file: &str,
        code: &str,
        line: usize,
        column: usize,
    ) -> PyResult<()> {
        Ok(())
    }
}
