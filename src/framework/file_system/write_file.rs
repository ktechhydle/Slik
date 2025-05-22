use pyo3::prelude::*;
use std::fs;

#[pyfunction]
pub fn write(file_name: &str, contents: &str) -> PyResult<()> {
    let _ = fs::write(file_name, contents)?;

    Ok(())
}
