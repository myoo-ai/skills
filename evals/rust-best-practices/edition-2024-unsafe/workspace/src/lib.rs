//! Small numeric helpers, also exported to our C code.

use std::os::raw::c_int;

extern "C" {
    fn abs(x: c_int) -> c_int;
}

static mut HISTORY: Vec<i32> = Vec::new();

/// Returns the absolute value of `x`, computed by libc, and records it.
pub fn c_abs(x: i32) -> i32 {
    unsafe {
        let r = abs(x);
        HISTORY.push(r);
        r
    }
}

/// Returns how many results `c_abs` has recorded.
pub fn history_len() -> usize {
    unsafe { HISTORY.len() }
}

/// Checksum of `len` bytes at `ptr`, for C callers.
#[no_mangle]
pub extern "C" fn checksum(ptr: *const u8, len: usize) -> u32 {
    let data = unsafe { std::slice::from_raw_parts(ptr, len) };
    sum(data)
}

/// Checksum of `len` bytes at `ptr`.
pub unsafe fn sum_raw(ptr: *const u8, len: usize) -> u32 {
    let data = std::slice::from_raw_parts(ptr, len);
    sum(data)
}

/// Checksum of a byte slice.
pub fn sum(data: &[u8]) -> u32 {
    data.iter()
        .fold(7u32, |acc, &b| acc.wrapping_mul(31).wrapping_add(b as u32))
}

/// Adds one to every value.
pub fn bump_all(values: &mut [u32]) {
    let p = values.as_mut_ptr();
    for i in 0..values.len() {
        unsafe {
            *p.add(i) += 1;
        }
    }
}
