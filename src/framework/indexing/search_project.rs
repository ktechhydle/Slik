use crate::framework::indexing::is_x::is_binary_file;
use crate::framework::indexing::should_skip::should_skip_dir;
use pyo3::prelude::*;
use walkdir::WalkDir;

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
            let file_name = path.to_string_lossy().to_string();
            let searchable_name = path
                .file_name()
                .expect("Error converting path to string")
                .to_string_lossy()
                .to_string();

            if searchable_name
                .to_lowercase()
                .as_str()
                .contains(query.to_lowercase().as_str())
            {
                results.push(file_name);
            }
        }
    }

    Ok(results)
}
