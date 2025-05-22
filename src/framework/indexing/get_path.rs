use crate::framework::indexing::is_x::is_virtualenv_dir;
use pyo3::prelude::*;
use walkdir::WalkDir;

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
