use textnorm::{normalize_all, normalize_whitespace};

const CASES: &[(&str, &str)] = &[
    ("", ""),
    ("abc", "abc"),
    ("a b c", "a b c"),
    ("  a  b  ", "a b"),
    ("a\t\tb\nc", "a b c"),
    ("a\u{00a0}\u{2003}b", "a b"),
    ("x \n", "x"),
    ("   ", ""),
    ("héllo  wörld", "héllo wörld"),
];

#[test]
fn grader_same_output() {
    for &(input, want) in CASES {
        let got = normalize_whitespace(input);
        let got: &str = &got;
        assert_eq!(got, want, "normalize_whitespace({input:?})");
        let owned = input.to_string();
        let got = normalize_whitespace(&owned);
        assert_eq!(&*got, want, "normalize_whitespace(&String {input:?})");
    }
    let lines: Vec<String> = CASES.iter().map(|(i, _)| (*i).to_string()).collect();
    let got: Vec<String> = normalize_all(&lines).into_iter().map(|s| s.to_string()).collect();
    let want: Vec<String> = CASES.iter().map(|(_, w)| (*w).to_string()).collect();
    assert_eq!(got, want);
    let arr = ["a  b".to_string(), "c".to_string()];
    let got: Vec<String> = normalize_all(&arr[..]).into_iter().map(|s| s.to_string()).collect();
    assert_eq!(got, ["a b", "c"]);
}

#[test]
fn grader_clean_input_not_copied() {
    for input in ["abc", "a b c", "already normalized text", "héllo wörld"] {
        let got = normalize_whitespace(input);
        let got: &str = &got;
        assert_eq!(got.as_ptr(), input.as_ptr(), "normalize_whitespace({input:?}) copied clean input");
    }
    let lines = vec!["clean line".to_string(), "dirty  line".to_string()];
    let out = normalize_all(&lines);
    let first = out.into_iter().next().expect("one result per line");
    let first: &str = &first;
    assert_eq!(first.as_ptr(), lines[0].as_ptr(), "normalize_all copied a clean line");
}
