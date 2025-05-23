use lsp_types;
use pyo3::prelude::*;

#[pyfunction]
pub fn open_document(file: &str) -> PyResult<()> {
    Ok(())
}

#[pyfunction]
pub fn close_document(file: &str) -> PyResult<()> {
    Ok(())
}

#[pyfunction]
pub fn get_document_completions(
    file: &str,
    code: &str,
    line: usize,
    column: usize,
) -> PyResult<Vec<String>> {
    Ok(vec!["greet(name: str)".to_string()])
}

#[pyfunction]
pub fn get_document_definitions(
    file: &str,
    code: &str,
    line: usize,
    column: usize,
) -> PyResult<()> {
    Ok(())
}

#[pyfunction]
pub fn get_document_usages(file: &str, code: &str, line: usize, column: usize) -> PyResult<()> {
    Ok(())
}

#[pyfunction]
pub fn format_document(file: &str, code: &str, line: usize, column: usize) -> PyResult<()> {
    Ok(())
}

#[pyfunction]
pub fn lint_document(file: &str, code: &str, line: usize, column: usize) -> PyResult<()> {
    Ok(())
}
