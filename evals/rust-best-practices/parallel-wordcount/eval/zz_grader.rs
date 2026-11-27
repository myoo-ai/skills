use std::collections::HashMap;

fn corpus() -> Vec<String> {
    let words = ["alpha", "Beta", "GAMMA", "delta", "beta", "épée", "ÉPÉE", "x"];
    (0..2_000)
        .map(|i| {
            let n = i % 7;
            (0..n)
                .map(|j| words[(i * 31 + j * 7) % words.len()])
                .collect::<Vec<_>>()
                .join(if i % 3 == 0 { "  \t" } else { " " })
        })
        .collect()
}

#[test]
fn grader_parallel_matches_sequential() {
    let lines = corpus();
    let want = wordstats::word_counts(&lines);
    for threads in [0, 1, 2, 3, 8, 64, 5_000] {
        let got: HashMap<String, usize> = wordstats::word_counts_parallel(&lines, threads);
        assert_eq!(got, want, "threads = {threads}");
    }
    for small in [&lines[..0], &lines[..1], &lines[..5]] {
        let want = wordstats::word_counts(small);
        for threads in [0, 1, 4, 16] {
            assert_eq!(wordstats::word_counts_parallel(small, threads), want, "{} lines, threads = {threads}", small.len());
        }
    }
    let total: usize = want.values().sum();
    let words: usize = lines.iter().map(|l| l.split_whitespace().count()).sum();
    assert_eq!(total, words);
    assert_eq!(want["épée"], lines.iter().flat_map(|l| l.split_whitespace()).filter(|w| w.to_lowercase() == "épée").count());
}
