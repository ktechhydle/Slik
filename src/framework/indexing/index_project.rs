use crate::framework::indexing::hash_file::hash;
use crate::framework::indexing::is_x::is_binary_file;
use crate::framework::indexing::should_skip::should_skip_dir;
use pyo3::prelude::*;
use walkdir::WalkDir;

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
            if let Ok(hash) = hash(path) {
                results.push((path.display().to_string(), hash));
            }
        }
    }

    Ok(results)
}
