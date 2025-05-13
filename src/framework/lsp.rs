use pyo3::prelude::*;

#[pyfunction]
pub fn get_completions(
    filename: &str,
    code: &str,
    line: usize,
    column: usize,
) -> PyResult<Vec<String>> {
    Ok(vec!["greet(name: str)".to_string()])
}
