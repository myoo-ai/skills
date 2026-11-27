#![allow(unused_unsafe, reason = "checksum may be a safe or an unsafe fn")]

fn reference_sum(data: &[u8]) -> u32 {
    data.iter()
        .fold(7u32, |acc, &b| acc.wrapping_mul(31).wrapping_add(u32::from(b)))
}

#[test]
fn grader_same_results() {
    for x in [0, 1, -1, 42, -42, i32::MAX, -i32::MAX] {
        assert_eq!(numffi::c_abs(x), x.abs(), "c_abs({x})");
    }
    for data in [&b""[..], b"a", b"hello world", &[0xff; 300][..]] {
        let want = reference_sum(data);
        assert_eq!(numffi::sum(data), want);
        // SAFETY: the pointer and length come from a live slice.
        assert_eq!(unsafe { numffi::sum_raw(data.as_ptr(), data.len()) }, want);
        // SAFETY: the pointer and length come from a live slice.
        assert_eq!(unsafe { numffi::checksum(data.as_ptr(), data.len()) }, want);
    }
    // SAFETY: C callers may pass NULL with length 0.
    assert_eq!(unsafe { numffi::checksum(std::ptr::null(), 0) }, reference_sum(&[]));
    let mut v = vec![0, 1, u32::MAX - 1, 9];
    numffi::bump_all(&mut v);
    assert_eq!(v, [1, 2, u32::MAX, 10]);
}

#[test]
fn grader_history_from_many_threads() {
    let before = numffi::history_len();
    std::thread::scope(|s| {
        for t in 0..8 {
            s.spawn(move || {
                for i in 0..2_000 {
                    assert_eq!(numffi::c_abs(-(t * 2_000 + i)), t * 2_000 + i);
                }
            });
        }
    });
    assert!(numffi::history_len() >= before + 16_000, "lost history entries");
}
