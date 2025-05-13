use pyo3::prelude::*;
use std::fs;
use std::io::{BufReader, Read};
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

    for entry in WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !should_skip_dir(e)) // only skip __pycache__
        .filter_map(Result::ok)
    {
        let path = entry.path();

        if entry.file_type().is_file() && !is_binary_file(path) {
            paths.push(path.display().to_string());
        }
    }

    Ok(paths)
}

// skip dirs
fn should_skip_dir(entry: &DirEntry) -> bool {
    entry.file_type().is_dir()
        && entry
            .file_name()
            .to_str()
            .map(|name| {
                [
                    "__pycache__",
                    "git",
                    "idea",
                    "vscode",
                    "venv",
                    "env",
                    "target",
                    "build",
                    "dist",
                ]
                .contains(&name)
            })
            .unwrap_or(false)
}

// check if a file contains binary content
fn is_binary_file(path: &std::path::Path) -> bool {
    if let Ok(file) = fs::File::open(path) {
        let mut reader = BufReader::new(file);
        let mut buffer = [0; 1024];
        if let Ok(n) = reader.read(&mut buffer) {
            // try to decode as UTF-8
            std::str::from_utf8(&buffer[..n]).is_err()
        } else {
            true
        }
    } else {
        true
    }
}
