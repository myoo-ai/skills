//! Chat bot commands.

/// A parsed chat command.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Command {
    Help,
    Remind { minutes: u32, text: String },
    Mute { user: String, hours: Option<u32> },
    Roll { sides: u32 },
}

/// Why a message is not a valid command.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError {
    NotACommand,
    Unknown(String),
    MissingArgument(&'static str),
    BadNumber(String),
}

/// Parses a chat message such as `/remind 10 stand up` into a command.
pub fn parse(input: &str) -> Result<Command, ParseError> {
    let input = input.trim();
    if input.starts_with('/') {
        let rest = &input[1..];
        let mut parts = rest.splitn(2, ' ');
        match parts.next() {
            Some(name) if !name.is_empty() => {
                let args = match parts.next() {
                    Some(a) => a.trim(),
                    None => "",
                };
                if name == "help" {
                    return Ok(Command::Help);
                } else if name == "remind" {
                    let mut it = args.splitn(2, ' ');
                    match it.next() {
                        Some(m) if !m.is_empty() => match m.parse::<u32>() {
                            Ok(minutes) => match it.next() {
                                Some(text) => {
                                    if !text.trim().is_empty() {
                                        return Ok(Command::Remind {
                                            minutes,
                                            text: text.trim().to_string(),
                                        });
                                    } else {
                                        return Err(ParseError::MissingArgument("text"));
                                    }
                                }
                                None => return Err(ParseError::MissingArgument("text")),
                            },
                            Err(_) => return Err(ParseError::BadNumber(m.to_string())),
                        },
                        _ => return Err(ParseError::MissingArgument("minutes")),
                    }
                } else if name == "mute" {
                    let mut it = args.split_whitespace();
                    match it.next() {
                        Some(user) => {
                            if user.starts_with('@') && user.len() > 1 {
                                match it.next() {
                                    Some(h) => match h.parse::<u32>() {
                                        Ok(hours) => {
                                            return Ok(Command::Mute {
                                                user: user[1..].to_string(),
                                                hours: Some(hours),
                                            });
                                        }
                                        Err(_) => return Err(ParseError::BadNumber(h.to_string())),
                                    },
                                    None => {
                                        return Ok(Command::Mute {
                                            user: user[1..].to_string(),
                                            hours: None,
                                        });
                                    }
                                }
                            } else {
                                return Err(ParseError::MissingArgument("user"));
                            }
                        }
                        None => return Err(ParseError::MissingArgument("user")),
                    }
                } else if name == "roll" {
                    if args.is_empty() {
                        return Ok(Command::Roll { sides: 6 });
                    } else {
                        match args.strip_prefix('d') {
                            Some(n) => match n.parse::<u32>() {
                                Ok(sides) if sides >= 2 => return Ok(Command::Roll { sides }),
                                _ => return Err(ParseError::BadNumber(args.to_string())),
                            },
                            None => return Err(ParseError::BadNumber(args.to_string())),
                        }
                    }
                } else {
                    return Err(ParseError::Unknown(name.to_string()));
                }
            }
            _ => return Err(ParseError::NotACommand),
        }
    } else {
        return Err(ParseError::NotACommand);
    }
}

/// Returns the help line shown for a command.
pub fn describe(cmd: &Command) -> String {
    match cmd {
        Command::Remind { minutes, .. } => format!("reminds you in {minutes} minutes"),
        Command::Mute { user, .. } => format!("mutes {user}"),
        _ => "shows help or rolls a die".to_string(),
    }
}
