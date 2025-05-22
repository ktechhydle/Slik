use sha1::{Digest, Sha1};
use std::fs;
use std::io::{BufReader, Read};
use std::path::Path;

pub fn hash(path: &Path) -> Result<String, std::io::Error> {
    let file = fs::File::open(path)?;
    let mut hasher = Sha1::new();
    let mut buffer = [0; 8192];
    let mut reader = BufReader::new(file);

    loop {
        let bytes_read = reader.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        hasher.update(&buffer[..bytes_read]);
    }

    Ok(format!("{:x}", hasher.finalize()))
}
