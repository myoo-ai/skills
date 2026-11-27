use std::error::Error;
use std::io;
use std::path::PathBuf;

fn temp_path(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("kvconf-grader-{}", std::process::id()));
    std::fs::create_dir_all(&dir).expect("create temp dir");
    dir.join(name)
}

fn library_error<E: Error + Send + Sync + 'static>(e: E) -> Box<dyn Error + Send + Sync> {
    Box::new(e)
}

fn check_message(what: &str, e: &(dyn Error + Send + Sync)) {
    let msg = e.to_string();
    let first = msg.chars().next().expect("error message is empty");
    assert!(!first.is_uppercase(), "{what}: message {msg:?} should start lowercase");
    assert!(!msg.ends_with(['.', '!']), "{what}: message {msg:?} should not end with punctuation");
}

#[test]
fn grader_valid_config() {
    let cfg = kvconf::parse("# web\nname = web\n\nport = 8080\n").expect("valid config");
    assert_eq!((cfg.name.as_str(), cfg.port, cfg.workers), ("web", 8080, 4));
    let cfg = kvconf::parse("name=a\nport=1\nworkers=9").expect("valid config");
    assert_eq!(cfg.workers, 9);

    let path = temp_path("ok.conf");
    std::fs::write(&path, "name = x\nport = 9\n").expect("write config");
    let cfg = kvconf::load(&path).expect("load valid config");
    assert_eq!((cfg.name.as_str(), cfg.port), ("x", 9));
}

#[test]
fn grader_invalid_configs_are_errors() {
    for text in [
        "",
        "port = 80",
        "name = x",
        "name = x\nport = 99999",
        "name = x\nport = http",
        "name = x\nport = 80\nworkers = many",
        "name = x\nport = 80\njust some words",
    ] {
        let e = library_error(kvconf::parse(text).expect_err(text));
        check_message(text, e.as_ref());
        if let Some(src) = e.source() {
            assert!(src.downcast_ref::<io::Error>().is_none(), "{text:?}: invalid content reported as an io error");
        }
    }
}

#[test]
fn grader_missing_file_keeps_io_cause() {
    let path = temp_path("does-not-exist.conf");
    let e = library_error(kvconf::load(&path).expect_err("missing file"));
    check_message("missing file", e.as_ref());
    assert!(e.to_string().contains("does-not-exist.conf"), "message {:?} should name the file", e.to_string());
    let io = e
        .source()
        .and_then(|s| s.downcast_ref::<io::Error>())
        .expect("source() of a read failure should be the io::Error");
    assert_eq!(io.kind(), io::ErrorKind::NotFound);
}

#[test]
fn grader_cause_not_repeated_in_message() {
    let path = temp_path("also-missing.conf");
    let e = library_error(kvconf::load(&path).expect_err("missing file"));
    let io = e
        .source()
        .and_then(|s| s.downcast_ref::<io::Error>())
        .expect("source() of a read failure should be the io::Error");
    let msg = e.to_string();
    assert!(!msg.contains(&io.to_string()), "message {msg:?} repeats its source {io}");
}
