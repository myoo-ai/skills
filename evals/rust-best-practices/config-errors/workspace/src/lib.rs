use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// Settings read from a `key = value` file.
#[derive(Debug, Clone, PartialEq)]
pub struct Config {
    pub name: String,
    pub port: u16,
    pub workers: usize,
}

/// Loads a config file. Blank lines and lines starting with `#` are skipped.
/// `name` and `port` are required, `workers` defaults to 4.
pub fn load(path: &Path) -> Result<Config, String> {
    let text = fs::read_to_string(path).map_err(|e| format!("Cannot read {}: {}.", path.display(), e))?;
    parse(&text)
}

/// Parses the contents of a config file.
pub fn parse(text: &str) -> Result<Config, String> {
    let mut values = HashMap::new();
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let (key, value) = line.split_once('=').unwrap();
        values.insert(key.trim().to_string(), value.trim().to_string());
    }
    let name = values.get("name").unwrap().clone();
    let port = values.get("port").unwrap().parse::<u16>().unwrap();
    let workers = match values.get("workers") {
        Some(w) => w.parse().map_err(|_| "Invalid workers.".to_string())?,
        None => 4,
    };
    Ok(Config { name, port, workers })
}
