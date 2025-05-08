use pyo3::prelude::*;


#[pyfunction]
pub fn get_completions(filename: &str, language: &str, code: &str, line: u8, column: u8) -> PyResult<Vec<&str>> {

    Ok(vec!["test"])
}
