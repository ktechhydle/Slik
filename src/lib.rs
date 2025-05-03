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
    m.add_function(wrap_pyfunction!(framework::completer::get_completions, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file::read, m)?)?;
    m.add_function(wrap_pyfunction!(framework::file::write, m)?)?;

    Ok(())
}
