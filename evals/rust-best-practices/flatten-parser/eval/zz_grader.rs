// Compares parse and describe with the original implementation.
#[allow(dead_code, clippy::all)]
#[path = "../../original/src/lib.rs"]
mod original;

const INPUTS: &[&str] = &[
    "",
    "hello",
    "/",
    "/ help",
    "  /help  ",
    "/help me",
    "/helpx",
    "/remind",
    "/remind ",
    "/remind 10",
    "/remind 10 ",
    "/remind 10 stand up",
    "/remind  10 stand up",
    "/remind ten stand up",
    "/remind -1 x",
    "/remind 99999999999 x",
    "/remind 5   spaced   text  ",
    "/mute",
    "/mute bob",
    "/mute @",
    "/mute @bob",
    "/mute @bob 3",
    "/mute @bob three",
    "/mute @bob 3 extra",
    "/mute   @bob\t4",
    "/roll",
    "/roll d20",
    "/roll d1",
    "/roll d",
    "/roll 20",
    "/roll dx",
    "/roll d6 d8",
    "/dance",
    "/REMIND 1 x",
    "/mute @ü 2",
    "/remind 3 \u{fc}n\u{ef}code \u{2713}",
];

#[test]
fn grader_same_behavior() {
    for input in INPUTS {
        let got = flatbot::parse(input);
        let want = original::parse(input);
        assert_eq!(format!("{got:?}"), format!("{want:?}"), "parse({input:?})");
        if let (Ok(g), Ok(w)) = (&got, &want) {
            assert_eq!(flatbot::describe(g), original::describe(w), "describe({g:?})");
        }
    }
}
