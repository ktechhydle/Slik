use pyo3::prelude::*;

#[pyfunction]
pub fn get_completions(
    filename: &str,
    code: &str,
    line: u8,
    column: u8,
) -> PyResult<Vec<String>> {
    Ok(vec!["greet(name: str)".to_string()])
}
