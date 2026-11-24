import platform
import re
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

# Allows importing the "src" package from the project root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import allure  # noqa: E402
from behave.model_core import Status  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402

from src.config.settings import get_settings  # noqa: E402
from src.enums import TracingMode  # noqa: E402
from src.interactors.shopping_interactor import ShoppingInteractor  # noqa: E402

REPORTS_DIR = ROOT_DIR / "reports"
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
ALLURE_REPORT_DIR = REPORTS_DIR / "allure-report"
TRACES_DIR = REPORTS_DIR / "traces"
VIDEOS_DIR = REPORTS_DIR / "videos"
VIEWPORT = {"width": 1366, "height": 900}


def _clean_dir(directory: Path) -> None:
    """Delete the contents (not the folder: the Allure formatter already created and uses it)."""
    directory.mkdir(parents=True, exist_ok=True)
    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _write_allure_environment(context) -> None:
    """Data shown by Allure in the report's 'Environment' widget."""
    settings = context.settings
    properties = {
        "Base.URL": settings.base_url,
        "Browser": f"{settings.browser} {context.browser.version}"
        + (f" ({settings.browser_channel})" if settings.browser_channel else ""),
        "Headless": settings.headless,
        "Playwright": version("playwright"),
        "Python": platform.python_version(),
        "OS": f"{platform.system()} {platform.release()}",
    }
    content = "\n".join(f"{key}={value}" for key, value in properties.items())
    (ALLURE_RESULTS_DIR / "environment.properties").write_text(content + "\n", encoding="utf-8")


def _console(message: str) -> None:
    """Print straight to the console: behave captures stdout inside hooks."""
    print(message, file=sys.__stdout__, flush=True)


def _allure_enabled(context) -> bool:
    """True when the Allure formatter is active (it is not when running e.g. with -f plain)."""
    return any("allure" in fmt.lower() for fmt in context.config.format or [])


def _generate_allure_report() -> None:
    """Regenerate the HTML report so `allure open` always shows the latest run.

    Requires the Allure CLI on PATH; if it is missing, the run is not affected.
    """
    allure_cli = shutil.which("allure")
    if not allure_cli:
        _console("\nAllure CLI not found on PATH: HTML report not generated.")
        return
    result = subprocess.run(
        [allure_cli, "generate", str(ALLURE_RESULTS_DIR), "-o", str(ALLURE_REPORT_DIR), "--clean"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        _console(f"\nAllure report generated: {ALLURE_REPORT_DIR}")
    else:
        _console(f"\nAllure report could not be generated:\n{result.stdout}{result.stderr}")


def _file_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:120]


# ---------------------------------------------------------------- hooks
def before_all(context):
    context.settings = get_settings()
    settings = context.settings
    for directory in (TRACES_DIR, VIDEOS_DIR):
        _clean_dir(directory)

    # expect() has its own timeout (5 s by default): use the same one as the browser actions.
    expect.set_options(timeout=settings.timeout_ms)
    context.playwright = sync_playwright().start()
    launcher = getattr(context.playwright, settings.browser)
    context.browser = launcher.launch(
        headless=settings.headless,
        slow_mo=settings.slow_mo,
        channel=settings.browser_channel,
    )

    if _allure_enabled(context):
        _clean_dir(ALLURE_RESULTS_DIR)
        _write_allure_environment(context)


def before_scenario(context, scenario):
    """Each scenario gets a new browser context: its own cookies, so its own empty cart."""
    settings = context.settings
    options = {"viewport": VIEWPORT}
    if settings.record_video:
        options["record_video_dir"] = str(VIDEOS_DIR)
        options["record_video_size"] = VIEWPORT
    context.browser_context = context.browser.new_context(**options)
    context.browser_context.set_default_timeout(settings.timeout_ms)
    context.browser_context.set_default_navigation_timeout(settings.timeout_ms)
    if settings.tracing != TracingMode.OFF:
        context.browser_context.tracing.start(screenshots=True, snapshots=True, sources=True, title=scenario.name)
    context.page = context.browser_context.new_page()

    context.shopping = ShoppingInteractor(context.page)
    context.added_products = []
    context.cart = None
    context.customer = None
    context.order = None


def after_step(context, step):
    """Screenshot after every step (red steps included) as evidence in the report."""
    page = getattr(context, "page", None)
    if page is None or page.is_closed():
        return
    try:
        name = "Screenshot" if step.status == Status.passed else "Screenshot on failure"
        allure.attach(page.screenshot(full_page=True), name=name, attachment_type=allure.attachment_type.PNG)
        if step.status == Status.failed:
            allure.attach(page.url, name="URL on failure", attachment_type=allure.attachment_type.TEXT)
            allure.attach(page.content(), name="HTML on failure", attachment_type=allure.attachment_type.HTML)
    except Exception as exc:  # evidence must never hide the real result
        _console(f"Could not capture evidence: {exc}")


def after_scenario(context, scenario):
    settings = context.settings
    failed = scenario.status == Status.failed
    base_name = _file_name(scenario.name)

    if settings.tracing != TracingMode.OFF:
        keep = settings.tracing == TracingMode.ALWAYS or failed
        trace_path = TRACES_DIR / f"{base_name}.zip"
        context.browser_context.tracing.stop(path=str(trace_path) if keep else None)
        if keep:
            allure.attach.file(str(trace_path), name="Playwright trace (open with: playwright show-trace)",
                               extension="zip")

    video = context.page.video
    context.browser_context.close()
    if video:
        video_path = VIDEOS_DIR / f"{base_name}.webm"
        video.save_as(str(video_path))
        video.delete()
        allure.attach.file(str(video_path), name="Video", attachment_type=allure.attachment_type.WEBM)


def after_all(context):
    browser = getattr(context, "browser", None)
    if browser:
        browser.close()
    playwright = getattr(context, "playwright", None)
    if playwright:
        playwright.stop()
    if _allure_enabled(context):
        _generate_allure_report()
