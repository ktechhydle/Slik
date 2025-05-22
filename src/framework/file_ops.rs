use pyo3::prelude::*;
use sha1::{Digest, Sha1};
use std::fs;
use std::io::{BufReader, Read};
use std::path::Path;
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
pub fn search(project_dir: &str, query: &str) -> PyResult<Vec<String>> {
    let mut results = Vec::new();

    for entry in WalkDir::new(project_dir)
        .into_iter()
        .filter_entry(|e| !should_skip_dir(e))
        .filter_map(Result::ok)
    {
        let path = entry.path();

        if entry.file_type().is_file() && !is_binary_file(path) {
            let file_name = path.display().to_string();

            if file_name.contains(query.to_lowercase().as_str()) {
                results.push(file_name);
            }
        }
    }

    Ok(results)
}

#[pyfunction]
pub fn index(dir: &str) -> PyResult<Vec<(String, String)>> {
    let mut results = Vec::new();

    for entry in WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !should_skip_dir(e))
        .filter_map(Result::ok)
    {
        let path = entry.path();

        if entry.file_type().is_file() && !is_binary_file(path) {
            if let Ok(hash) = hash_file(path) {
                results.push((path.display().to_string(), hash));
            }
        }
    }

    Ok(results)
}

#[pyfunction]
pub fn get_python_path(dir: &str) -> PyResult<String> {
    let mut python_path = String::new();

    for entry in WalkDir::new(dir).into_iter().filter_map(Result::ok) {
        let path = entry.path();

        if is_virtualenv_dir(path) {
            python_path.push_str(
                path.join("Scripts")
                    .join("python.exe")
                    .to_string_lossy()
                    .to_string()
                    .as_str(),
            );
        }
    }

    if python_path.is_empty() {
        python_path.push_str("python");
    }

    Ok(python_path)
}

fn should_skip_dir(entry: &DirEntry) -> bool {
    let name = entry.file_name().to_str();

    let is_named_to_skip = name
        .map(|name| {
            [
                "__pycache__",
                ".git",
                ".idea",
                ".vscode",
                "target",
                "build",
                "dist",
            ]
            .contains(&name)
        })
        .unwrap_or(false);

    let is_venv = is_virtualenv_dir(entry.path());

    entry.file_type().is_dir() && (is_named_to_skip || is_venv)
}

fn is_binary_file(path: &Path) -> bool {
    if let Ok(file) = fs::File::open(path) {
        let mut reader = BufReader::new(file);
        let mut buffer = [0; 1024];
        if let Ok(n) = reader.read(&mut buffer) {
            std::str::from_utf8(&buffer[..n]).is_err()
        } else {
            true
        }
    } else {
        true
    }
}

fn is_virtualenv_dir(path: &Path) -> bool {
    path.join("pyvenv.cfg").exists()
}

fn hash_file(path: &Path) -> Result<String, std::io::Error> {
    let file = fs::File::open(path)?;
    let mut hasher = Sha1::new();
    let mut buffer = [0; 8192];
    let mut reader = BufReader::new(file);

    loop {
        let bytes_read = reader.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
    }

    Ok(format!("{:x}", hasher.finalize()))
}
