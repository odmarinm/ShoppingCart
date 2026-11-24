from enum import StrEnum


class Browser(StrEnum):
    """Browser engines supported by Playwright."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class TracingMode(StrEnum):
    """When a Playwright trace is kept and attached to the Allure report."""

    ALWAYS = "always"
    ON_FAILURE = "on_failure"
    OFF = "off"
