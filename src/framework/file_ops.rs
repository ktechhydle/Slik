use pyo3::prelude::*;
use std::fs;
use walkdir::WalkDir;

#[pyfunction]
pub fn read(file_name: &str) -> PyResult<String> {
    let contents = fs::read_to_string(file_name)?;

    Ok(contents)
}

#[pyfunction]
pub fn write(file_name: &str, contents: &str) -> PyResult<()> {
    let _ = fs::write(file_name, contents)?;

    Ok(())
}

#[pyfunction]
pub fn index(dir: &str) -> PyResult<Vec<String>> {
    let mut paths = Vec::new();

    for entry in WalkDir::new(dir).into_iter().filter_map(Result::ok) {
        if entry.file_type().is_file() {
            paths.push(entry.path().display().to_string());
        }
    }

    Ok(paths)
}