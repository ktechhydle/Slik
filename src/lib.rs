use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
mod framework;

// Test function to test if the bindings are correct
#[pyfunction]
fn test() -> PyResult<()> {
    println!("Hello from Rust!");

    Ok(())
}

#[pymodule]
fn slik(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, m)?)?;
    m.add_function(wrap_pyfunction!(framework::lsp::get_completions, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file_ops::read, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file_ops::write, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file_ops::search, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file_ops::index, m)?)?;

    Ok(())
}
