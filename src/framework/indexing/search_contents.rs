use crate::framework::indexing::is_x::is_binary_file;
use crate::framework::indexing::should_skip::should_skip_dir;
use pyo3::prelude::*;
use std::fs;
use walkdir::WalkDir;

#[pyfunction]
pub fn search_file_contents(
    project_dir: &str,
    query: &str,
) -> PyResult<Vec<(String, (usize, usize))>> {
    let mut results = Vec::new();

    for entry in WalkDir::new(project_dir)
        .into_iter()
        .filter_entry(|e| !should_skip_dir(e))
        .filter_map(Result::ok)
    {
        let path = entry.path();

        if entry.file_type().is_file() && !is_binary_file(path) {
            let file_name = path.to_string_lossy().to_string();
            let contents = fs::read_to_string(&file_name).expect("Error reading file");

            if let Some(position) = contents.find(query) {
                let mut line_num: usize = 0;
                let mut col_num: usize = 0;

                for (i, ch) in contents.chars().enumerate() {
                    if i == position {
                        results.push((file_name.to_string(), (line_num, col_num)));
                    }
                    if ch == '\n' {
                        line_num += 1;
                        col_num = 0;
                    } else {
                        col_num += 1;
                    }
                }
            }
        }
    }

    Ok(results)
}
