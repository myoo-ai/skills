//! Text clean-up helpers for the search indexer.

/// Trims `s` and collapses every run of whitespace into a single space.
pub fn normalize_whitespace(s: &String) -> String {
    let mut out = String::new();
    let mut in_space = false;
    for c in s.trim().chars() {
        if c.is_whitespace() {
            if !in_space {
                out.push(' ');
            }
            in_space = true;
        } else {
            out.push(c);
            in_space = false;
        }
    }
    out
}

/// Normalizes every line, see [`normalize_whitespace`].
pub fn normalize_all(lines: &Vec<String>) -> Vec<String> {
    let mut out = Vec::new();
    for i in 0..lines.len() {
        let line = lines[i].clone();
        out.push(normalize_whitespace(&line));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn collapses_whitespace() {
        assert_eq!(normalize_whitespace(&" a \t b\n".to_string()), "a b");
    }
}
