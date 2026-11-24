# ShoppingCart - OpenCart E2E Automation

End-to-end (E2E) automated test of the purchase flow of the demo store
[OpenCart by Abstracta](http://opencart.abstracta.us/) with Python + Behave (Gherkin) + Playwright + Allure.

The scenario:

1. Adds two products to the cart (searching them in the catalog and opening each product page).
2. Views the shopping cart.
3. Completes the checkout as a guest ("Guest Checkout").
4. Confirms the order up to the message "Your order has been placed!".

## Prerequisites

| Tool                    | Needed for                         | Required |
|-------------------------|------------------------------------|----------|
| Python 3.11 or newer    | Running the tests                  | Yes      |
| Git                     | Cloning the repository             | Yes      |
| Internet access         | `http://opencart.abstracta.us` and downloading the browser | Yes |
| ~500 MB of free disk    | Dependencies + browser downloaded by Playwright | Yes |
| Java 8+ and Allure CLI  | Only to VIEW the HTML report       | No       |

The demo store is a public, shared server: it can be slow or fail at times even when the code
is correct.

### Install the prerequisites

Skip any tool you already have. Check what is installed with:

```
python --version      (macOS/Linux: python3 --version)
git --version
java -version         (optional)
allure --version      (optional)
```

**Windows** (PowerShell; `winget` comes with Windows 10/11):

```powershell
winget install --id Python.Python.3.13 --exact
winget install --id Git.Git --exact
```

Close and open the terminal again after installing, so the new commands are found.
If `python` opens the Microsoft Store or says "Python was not found", disable the aliases in
*Settings > Apps > Advanced app settings > App execution aliases* ("python.exe" and
"python3.exe"), or use `py` instead of `python` in all the commands below.
If you install Python from https://www.python.org/downloads/ instead, check
**"Add python.exe to PATH"** in the first screen of the installer.

**macOS** (with [Homebrew](https://brew.sh)):

```bash
brew install python git
```

**Linux (Debian / Ubuntu)**:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

The optional Java + Allure CLI installation is explained in
[View the Allure report](#view-the-allure-report).

## Quick start

For those who already have the prerequisites (Windows PowerShell; every step is explained in
[Setup](#setup) and [Run](#run)):

```powershell
git clone https://github.com/odmarinm/ShoppingCart.git
cd ShoppingCart
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium
copy .env.example .env
.\.venv\Scripts\behave
```

## Structure

```
features/                         .feature files (Gherkin), grouped by business area
  checkout/guest_checkout.feature
  steps/                          Steps: one file per area (catalog, cart, checkout)
    catalog_steps.py
    cart_steps.py
    checkout_steps.py
  environment.py                  Behave hooks: browser, screenshots, traces, Allure
src/
  config/settings.py              Reads the .env file
  enums/                          Route, CheckoutOption, PaymentMethod, StoreMessage, Browser
  builders/                       Build test data (GuestCustomerBuilder); never touch the browser
  models/                         Data read from the pages (AddedProduct, CartSummary, OrderResult...)
  interactors/                    Use cases called by the steps (ShoppingInteractor)
  pages/                          Page Object Model: the ONLY layer that uses Playwright
    base_page.py                  Navigation, header (search box, cart button), alerts
    catalog_page.py               Home page and search results
    product_page.py               Product page: price and "Add to Cart"
    cart_page.py                  Shopping cart: products and totals
    checkout_page.py              Checkout steps 1 to 6
    order_success_page.py         "Your order has been placed!" page
  validators/                     Validations of the data read (no Playwright)
  utils/                          Money parsing, assertions, Allure checker
```

Layer rule: `features → steps → interactors → pages`. Only `src/pages` uses Playwright.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/odmarinm/ShoppingCart.git
cd ShoppingCart
```

### 2. Create the virtual environment and install the dependencies

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Download the browser used by Playwright

Windows (PowerShell):

```powershell
.\.venv\Scripts\python -m playwright install chromium
```

macOS / Linux:

```bash
.venv/bin/python -m playwright install --with-deps chromium
```

The download is about 200 MB and is done only once. If it cannot be downloaded (for example
behind a corporate proxy), you can use a browser already installed on the machine instead:
set `BROWSER_CHANNEL=msedge` (or `chrome`) in the `.env` file (next step).

### 4. Create the `.env` file

Windows (PowerShell):

```powershell
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

The default values work as they are, so nothing needs to be changed:

| Variable          | Required | Description                                                                        |
|-------------------|----------|------------------------------------------------------------------------------------|
| `BASE_URL`        | Yes      | Store URL (default: `http://opencart.abstracta.us`)                                |
| `BROWSER`         | No       | `chromium` (default), `firefox` or `webkit`                                        |
| `BROWSER_CHANNEL` | No       | Use an installed browser: `msedge` or `chrome`. Empty = Playwright Chromium        |
| `HEADLESS`        | No       | `true` (default) runs without a window; `false` shows the browser                  |
| `SLOW_MO`         | No       | Milliseconds between actions, to watch the run (e.g. `500`). Default `0`           |
| `TIMEOUT`         | No       | Timeout of each browser action and check, in seconds (default: `45`)               |
| `TRACING`         | No       | Playwright trace per scenario: `always` (default), `on_failure` or `off`           |
| `RECORD_VIDEO`    | No       | `true` records a video of each scenario and attaches it to Allure (default `false`) |

To use Firefox or WebKit, download them first:

```powershell
.\.venv\Scripts\python -m playwright install firefox webkit      # macOS/Linux: .venv/bin/python -m ...
```

### 5. (Optional) Activate the virtual environment

All the commands in this README use the full path (`.\.venv\Scripts\...`), so activating the
environment is NOT needed. If you activate it, you can type the short commands instead
(`behave`, `playwright`, `pip`):

Windows (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned   # allows the activation script in this terminal only
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

The prompt then starts with `(.venv)`. Type `deactivate` to leave it. Visual Studio Code
runs these commands automatically when it opens a terminal in the project.

## Run

Always run the commands from the project root folder (where `behave.ini` is).

Windows (PowerShell):

```powershell
.\.venv\Scripts\behave                            # everything
.\.venv\Scripts\behave --tags=@guest_checkout     # a single family
```

macOS / Linux:

```bash
.venv/bin/behave                                  # everything
.venv/bin/behave --tags=@guest_checkout           # a single family
```

A successful run ends with:

```
1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

followed by `Allure report generated: ...` if the Allure CLI is installed, or by
`Allure CLI not found on PATH: HTML report not generated.` if it is not (only a notice).

To watch the browser while the test runs, set `HEADLESS=false` and `SLOW_MO=500` in `.env`.

Available tags:

| Tag               | Runs                                                       |
|-------------------|------------------------------------------------------------|
| `@checkout`       | All the checkout features                                  |
| `@guest_checkout` | Buy two products as a guest, up to the order confirmation  |

The scenario runs twice (Scenario Outline with 2 examples):

| Products                                | Guest address                  | Payment          |
|-----------------------------------------|--------------------------------|------------------|
| 1 x MacBook + 1 x iPhone                | Bogota D.C., Colombia          | Bank Transfer    |
| 1 x Samsung SyncMaster 941BW + 2 x Nikon D300 | Greater London, United Kingdom | Cash On Delivery |

A full run takes about 1-2 minutes, depending on how fast the demo server answers.

Every scenario uses a new browser context (its own cookies), so it always starts with an empty cart.

## Results and evidence

| Folder                    | Content                                                                        |
|---------------------------|--------------------------------------------------------------------------------|
| `reports/allure-results`  | Raw Allure results (cleared at the start of each run)                          |
| `reports/allure-report`   | HTML report, regenerated automatically at the end of each run (needs Allure CLI) |
| `reports/traces`          | One Playwright trace (`.zip`) per scenario                                     |
| `reports/videos`          | One video per scenario, only with `RECORD_VIDEO=true`                          |

In the Allure report, each scenario shows:

- Its Gherkin steps, with the page actions as sub-steps (e.g. "Search the catalog for 'MacBook'",
  "Step 5 - Pay with 'Cash On Delivery', accept the Terms & Conditions and continue").
- A **full-page screenshot** after every step. When a step fails: "Screenshot on failure",
  the page URL and its HTML.
- Every validation as a sub-step with the expected and actual values, for example
  `✔ Total (= Sub-Total $601.00 + Flat Shipping Rate $5.00): expected $606.00 | got $606.00`.
  All the checks run and a failure lists every value that did not match.
- The **Playwright trace** attached as a `.zip`.

### Open a Playwright trace

The trace shows each action with screenshots, DOM snapshots, network calls and console logs:

```powershell
.\.venv\Scripts\playwright show-trace reports\traces\<scenario>.zip      # macOS/Linux: .venv/bin/playwright ...
```

You can also drag the `.zip` file onto https://trace.playwright.dev (it is processed in the browser).

## View the Allure report

Requires Java (8 or newer) and the Allure CLI (2.x). Only needed to view the report: the tests
run and save their results without them.

**Windows** (PowerShell, as a normal user, not as Administrator):

```powershell
# 1. Java
winget install --id EclipseAdoptium.Temurin.21.JDK --exact

# 2. Scoop (package manager used to install Allure) - skip if `scoop --version` works
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# 3. Allure CLI
scoop install allure
```

**macOS**:

```bash
brew install allure         # also installs Java
```

**Linux (Debian / Ubuntu)**:

```bash
sudo apt install -y default-jre
```

Then download `allure-<version>.zip` from https://github.com/allure-framework/allure2/releases,
unzip it and add its `bin` folder to the PATH. This also works on any OS without a package manager.

Close and open the terminal again, then check the installation:

```
java -version
allure --version
```

If Allure says Java was not found, set the `JAVA_HOME` variable to the Java installation folder
(e.g. `C:\Program Files\Eclipse Adoptium\jdk-21...`) and open a new terminal.

Once installed, run the tests again (the HTML report is generated at the end of each run) and open it:

```bash
allure open reports/allure-report      # opens the HTML of the latest run (generated automatically)
allure serve reports/allure-results    # alternative: builds a temporary report and opens it
```

Do NOT open `reports/allure-report/index.html` by double-clicking it: browsers block the report
data when the file is opened from disk, and the report shows "Loading..." or a 404 error.
`allure open` starts a small local web server; stop it with `Ctrl+C` when you are done.

## Troubleshooting

| Problem                                                     | Solution                                                                  |
|-------------------------------------------------------------|---------------------------------------------------------------------------|
| `Executable doesn't exist ... playwright install`           | Run step 3 again, or set `BROWSER_CHANNEL=msedge` (or `chrome`)           |
| `Timeout 45000ms exceeded`                                  | The demo server is slow: run again or increase `TIMEOUT` in `.env`        |
| `Next checkout step did not open ...`                       | The store rejected a checkout step; the message includes the store errors |
| `net::ERR_...` or `Timeout` on the first step               | The demo server or the network did not answer: run again                  |
| `Allure CLI not found on PATH`                              | Only a notice: the tests ran. Install Allure to view the HTML report      |
| Allure report blank, "Loading..." or 404                    | Open it with `allure open reports/allure-report`, not by double-click     |
| `python` opens the Microsoft Store / "Python was not found" | Disable the App execution aliases, or use `py` instead of `python`        |
| `Activate.ps1 cannot be loaded ... running scripts is disabled` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first (or skip activation, see step 5) |
| `ModuleNotFoundError` / `behave` not recognized             | Run the commands from the project root, with the `.\.venv\Scripts\` prefix |
| `git clone` asks for credentials or says "not found"        | The repository must be public, or your GitHub user must have access to it |
