use std::fs;
use std::io::{BufReader, Read};
use std::path::Path;

pub fn is_binary_file(path: &Path) -> bool {
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

pub fn is_virtualenv_dir(path: &Path) -> bool {
    path.join("pyvenv.cfg").exists()
}
