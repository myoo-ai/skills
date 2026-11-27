use std::io::{self, BufRead, Write};

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let line = line?;
        let out = textnorm::normalize_whitespace(&line);
        writeln!(io::stdout(), "{}", out)?;
    }
    Ok(())
}
