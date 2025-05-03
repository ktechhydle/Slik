use pyo3::prelude::*;
use ra_ap_ide::{AnalysisHost, FileId, RootDatabase, CompletionConfig};
use ra_ap_vfs::{VfsPath, Vfs};
use ra_ap_base_db::{SourceDatabaseExt, FileLoader};
use ra_ap_ide_db::base_db::{FilePosition, FileRange, SourceDatabase};
use ra_ap_text_edit::TextRange;
use ra_ap_syntax::TextSize;
use std::sync::Arc;

#[pyfunction]
pub fn get_completions(code: &str, offset: usize) -> PyResult<Vec<String>> {
    // Create a new AnalysisHost (manages analysis state)
    let mut host = AnalysisHost::default();

    // Create a file ID and add our code to it
    let file_id = FileId(0);
    host.analysis_change().add_file(file_id, Arc::from(code.to_string()));

    // Commit the file to the database
    host.apply_change();

    // Request completions
    let position = FilePosition {
        file_id,
        offset: TextSize::try_from(offset).unwrap(),
    };

    let analysis = host.analysis();
    let completions = analysis.completions(&CompletionConfig::default(), position).unwrap_or(None);

    let items = match completions {
        Some(completion_items) => completion_items
            .into_iter()
            .map(|item| item.label().to_string())
            .collect(),
        None => vec![],
    };

    Ok(items)
}
