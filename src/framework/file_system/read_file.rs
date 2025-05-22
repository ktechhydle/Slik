use pyo3::prelude::*;
use std::fs;

#[pyfunction]
pub fn read(file_name: &str) -> PyResult<String> {
    let contents = fs::read_to_string(file_name)?;

    Ok(contents)
}
