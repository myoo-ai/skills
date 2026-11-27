//! Word statistics for the corpus tools.

use std::collections::HashMap;

/// Counts how often each word occurs in `lines`, ignoring case. Words are
/// separated by whitespace.
pub fn word_counts(lines: &[String]) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for line in lines {
        for word in line.split_whitespace() {
            let word = word.to_lowercase();
            if counts.contains_key(&word) {
                *counts.get_mut(&word).unwrap() += 1;
            } else {
                counts.insert(word, 1);
            }
        }
    }
    counts
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counts_words_ignoring_case() {
        let lines = vec!["The cat".to_string(), "the  dog THE".to_string()];
        let counts = word_counts(&lines);
        assert_eq!(counts["the"], 3);
        assert_eq!(counts["cat"], 1);
        assert_eq!(counts.len(), 3);
    }
}
