"""Runs every check as an Allure sub-step and reports all the failures together."""
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import allure

from src.utils.assertions import assert_equals, show


class Checker:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, title: str, error: str | None) -> None:
        """A check with a custom title; `error` is None when it passed."""
        icon = "✘ " if error else "✔ "
        try:
            with allure.step(icon + title):
                if error:
                    raise AssertionError(error)
        except AssertionError as exc:
            self.errors.append(str(exc))

    def equals(self, label: str, expected: Any, actual: Any) -> None:
        """assert_equals inside an Allure sub-step; on failure, record the error and continue."""
        icon = "✔ " if actual == expected else "✘ "
        title = f"{icon}{label}: expected {show(expected)} | got {show(actual)}"
        try:
            with allure.step(title):
                assert_equals(actual, expected, label)
        except AssertionError as exc:
            self.errors.append(str(exc))

    @staticmethod
    def info(title: str) -> None:
        """Informational step that never fails (a known site behavior worth seeing in the report)."""
        with allure.step(f"ℹ {title}"):
            pass

    @contextmanager
    def group(self, title: str) -> Iterator[None]:
        """Group checks; the group turns red if any of its checks fails."""
        errors_before = len(self.errors)
        try:
            with allure.step(title):
                yield
                failed = len(self.errors) - errors_before
                if failed:
                    raise AssertionError(f"{failed} check(s) failed")
        except AssertionError:
            pass  # errors are already in self.errors

    def raise_if_errors(self, operation: str) -> None:
        assert not self.errors, f"{operation} has errors:\n  - " + "\n  - ".join(self.errors)
