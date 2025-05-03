use pyo3::prelude::*;


#[pyfunction]
pub fn get_completions(code: &str, line: u8, index: u8) -> PyResult<Vec<String>> {

    Ok(vec![String::from("fn")])
}