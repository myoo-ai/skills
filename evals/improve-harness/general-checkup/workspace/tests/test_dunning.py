from datetime import date

import pytest

from billing.dunning import Reminder, next_reminder


@pytest.mark.parametrize(
    ("today", "want"),
    [
        (date(2026, 3, 1), Reminder.NONE),
        (date(2026, 3, 10), Reminder.FRIENDLY),
        (date(2026, 3, 25), Reminder.FINAL),
        (date(2026, 4, 15), Reminder.COLLECTIONS),
    ],
)
def test_next_reminder(today: date, want: Reminder) -> None:
    assert next_reminder(date(2026, 3, 1), today) is want
