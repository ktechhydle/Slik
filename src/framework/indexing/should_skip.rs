use super::is_x::is_virtualenv_dir;
use walkdir::DirEntry;

pub fn should_skip_dir(entry: &DirEntry) -> bool {
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
