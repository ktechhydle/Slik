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
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::open_document,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::close_document,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::get_document_completions,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::get_document_definitions,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::get_document_usages,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::format_document,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::language_server::lsp::lint_document,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::file_system::read_file::read,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::file_system::write_file::write,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::indexing::search_project::search,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::indexing::index_project::index,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        framework::indexing::get_path::get_python_path,
        m
    )?)?;

    Ok(())
}
