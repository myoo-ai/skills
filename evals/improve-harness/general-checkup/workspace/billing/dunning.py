"""Decide which reminder an unpaid invoice gets."""

from datetime import date
from enum import StrEnum


class Reminder(StrEnum):
    NONE = "none"
    FRIENDLY = "friendly"
    FINAL = "final"
    COLLECTIONS = "collections"


def next_reminder(due: date, today: date) -> Reminder:
    """Return the reminder to send for an invoice due on `due`."""
    overdue = (today - due).days
    if overdue <= 0:
        return Reminder.NONE
    if overdue <= 14:
        return Reminder.FRIENDLY
    if overdue <= 30:
        return Reminder.FINAL
    return Reminder.COLLECTIONS
