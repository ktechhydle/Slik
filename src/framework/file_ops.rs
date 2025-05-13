use pyo3::prelude::*;
use std::fs;
use walkdir::{DirEntry, WalkDir};

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

    fn is_hidden(entry: &DirEntry) -> bool {
        // skip any directory or file that starts with .
        if let Some(name) = entry.file_name().to_str() {
            name.starts_with(".")
        } else {
            false
        }
    }

    for entry in WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !is_hidden(e))
        .filter_map(Result::ok)
    {
        if entry.file_type().is_file() {
            paths.push(entry.path().display().to_string());
        }
    }

    Ok(paths)
}
