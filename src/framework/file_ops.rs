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
                    ".venv",
                    "venv",
                    ".env",
                    "env",
                    "target",
                    "build",
                    "dist",
                ]
                .contains(&name)
            })
            .unwrap_or(false)
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
