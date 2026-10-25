
import os
import sys
import secrets
import time
import math
import hmac

from fastapi import (
    FastAPI,
    Form,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.trustedhost import TrustedHostMiddleware


# =========================================================
# PROJECT PATHS AND DATABASE
# =========================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import (
    init_db,
    create_account as db_create_account,
    get_account,
    verify_account_pin,
    change_account_pin,
    apply_transaction,
    get_connection,
)


app = FastAPI(title="Dholakpur Banking System")

# Initialize the SQLite tables when the app starts.
init_db()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(APP_DIR, "static")),
    name="static",
)


# =========================================================
# CUSTOMER PIN VERIFICATION
# =========================================================

PIN_TOKEN_LIFETIME = 300
pin_verification_tokens = {}


def remove_expired_pin_tokens():
    current_time = time.monotonic()

    expired_tokens = [
        token
        for token, details in pin_verification_tokens.items()
        if current_time >= details["expires_at"]
    ]

    for token in expired_tokens:
        pin_verification_tokens.pop(token, None)


# =========================================================
# EXISTING CUSTOMER WEBSITE
# =========================================================

@app.get("/admin")
def home():
    return FileResponse(
        os.path.join(APP_DIR, "templates", "index.html")
    )


@app.post("/api/create-account")
def create_account(
    account_number: str = Form(...),
    name: str = Form(...),
    pin: str = Form(...),
):
    account_number = account_number.strip()
    name = name.strip()

    if not account_number:
        return {
            "success": False,
            "message": "Account number is required.",
        }

    if not name:
        return {
            "success": False,
            "message": "Name is required.",
        }

    if len(pin) != 4 or not pin.isdigit():
        return {
            "success": False,
            "message": "PIN must contain exactly 4 digits!",
        }

    created = db_create_account(account_number, name, pin)

    if not created:
        return {
            "success": False,
            "message": "Account already exists!",
        }

    return {
        "success": True,
        "message": f"Welcome to Dholakpur Banking, {name}!",
        "account_number": account_number,
        "name": name,
        "balance": 0,
    }


@app.post("/api/login")
def login(
    account_number: str = Form(...),
    pin: str = Form(...),
):
    account_number = account_number.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if not verify_account_pin(account_number, pin):
        return {
            "success": False,
            "message": "Incorrect PIN!",
        }

    account = get_account(account_number)

    return {
        "success": True,
        "message": "Login successful!",
        "account_number": account_number,
        "name": account["name"],
        "balance": account["balance"],
    }


@app.post("/api/account-details")
def account_details(
    account_number: str = Form(...),
    pin: str = Form(...),
):
    account_number = account_number.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if not verify_account_pin(account_number, pin):
        return {
            "success": False,
            "message": "Incorrect PIN!",
        }

    account = get_account(account_number)

    return {
        "success": True,
        "account_number": account_number,
        "name": account["name"],
        "balance": account["balance"],
    }


@app.post("/api/balance")
def check_balance(
    account_number: str = Form(...),
    pin: str = Form(...),
):
    account_number = account_number.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if not verify_account_pin(account_number, pin):
        return {
            "success": False,
            "message": "Incorrect PIN!",
        }

    account = get_account(account_number)

    return {
        "success": True,
        "balance": account["balance"],
    }


@app.post("/api/deposit")
def deposit(
    account_number: str = Form(...),
    pin: str = Form(...),
    amount: float = Form(...),
):
    account_number = account_number.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if not verify_account_pin(account_number, pin):
        return {
            "success": False,
            "message": "Incorrect PIN!",
        }

    if not math.isfinite(amount) or amount <= 0:
        return {
            "success": False,
            "message": "Invalid amount!",
        }

    status, new_balance = apply_transaction(
        account_number,
        "deposit",
        amount,
    )

    if status != "success":
        return {
            "success": False,
            "message": "Deposit could not be completed.",
        }

    return {
        "success": True,
        "message": "Deposit successful!",
        "amount": amount,
        "balance": new_balance,
    }


@app.post("/api/withdraw")
def withdraw(
    account_number: str = Form(...),
    pin: str = Form(...),
    amount: float = Form(...),
):
    account_number = account_number.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if not verify_account_pin(account_number, pin):
        return {
            "success": False,
            "message": "Incorrect PIN!",
        }

    if not math.isfinite(amount) or amount <= 0:
        return {
            "success": False,
            "message": "Invalid amount!",
        }

    status, result_balance = apply_transaction(
        account_number,
        "withdraw",
        amount,
    )

    if status == "insufficient_balance":
        return {
            "success": False,
            "message": "Insufficient balance!",
        }

    if status != "success":
        return {
            "success": False,
            "message": "Withdrawal could not be completed.",
        }

    return {
        "success": True,
        "message": "Withdrawal successful!",
        "amount": amount,
        "balance": result_balance,
    }


@app.post("/api/verify-pin-account")
def verify_pin_account(
    account_number: str = Form(...),
    name: str = Form(...),
):
    account_number = account_number.strip()
    name = name.strip()
    account = get_account(account_number)

    if account is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if name.casefold() != account["name"].strip().casefold():
        return {
            "success": False,
            "message": "Account name does not match!",
        }

    remove_expired_pin_tokens()

    verification_token = secrets.token_urlsafe(32)

    pin_verification_tokens[verification_token] = {
        "account_number": account_number,
        "expires_at": time.monotonic() + PIN_TOKEN_LIFETIME,
    }

    return {
        "success": True,
        "message": "Account verified successfully!",
        "account_number": account_number,
        "name": account["name"],
        "verification_token": verification_token,
        "expires_in": PIN_TOKEN_LIFETIME,
    }


@app.post("/api/change-pin")
def change_pin(
    verification_token: str = Form(...),
    new_pin: str = Form(...),
):
    verification_token = verification_token.strip()

    if not verification_token:
        return {
            "success": False,
            "message": "Verification required. Verify your account first.",
        }

    token_details = pin_verification_tokens.pop(
        verification_token,
        None,
    )

    if token_details is None:
        return {
            "success": False,
            "message": (
                "Invalid or already-used verification token. Verify again."
            ),
        }

    if time.monotonic() >= token_details["expires_at"]:
        return {
            "success": False,
            "message": (
                "Verification expired. Please verify your account again."
            ),
        }

    account_number = token_details["account_number"]

    if get_account(account_number) is None:
        return {
            "success": False,
            "message": "Account not found!",
        }

    if len(new_pin) != 4 or not new_pin.isdigit():
        return {
            "success": False,
            "message": (
                "PIN must contain exactly 4 digits. Please verify again."
            ),
        }

    if not change_account_pin(account_number, new_pin):
        return {
            "success": False,
            "message": "PIN could not be changed. Please verify again.",
        }

    return {
        "success": True,
        "message": "Your PIN has been changed successfully!",
    }


# =========================================================
# ADMIN AUTHENTICATION
# =========================================================
# Set these environment variables before starting Uvicorn:
# BANK_ADMIN_USERNAME
# BANK_ADMIN_PASSWORD
#
# Do not hardcode admin credentials in this file.

ADMIN_USERNAME = os.environ.get("BANK_ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("BANK_ADMIN_PASSWORD")

admin_security = HTTPBasic()


def require_admin(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(admin_security),
):
    # Avoid accidentally accepting credentials when not configured.
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=503,
            detail="Admin credentials are not configured.",
        )

    username_correct = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        ADMIN_USERNAME.encode("utf-8"),
    )
    password_correct = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        ADMIN_PASSWORD.encode("utf-8"),
    )

    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )

    # HTTP Basic sends credentials with every request. Prevent browser
    # and intermediary caching of private dashboard responses.
    return credentials.username


# =========================================================
# ADMIN DASHBOARD PAGE
# =========================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    admin: str = Depends(require_admin),
):
    response = HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dholakpur | Admin Dashboard</title>
<style>
    * { box-sizing: border-box; }

    body {
        margin: 0;
        padding: 28px;
        font-family: Arial, sans-serif;
        background: #f3f5fa;
        color: #172033;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 26px;
    }

    h1 { margin: 0 0 8px; }
    p { color: #657089; }

    .cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 16px;
        margin-bottom: 26px;
    }

    .card, .panel {
        background: white;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 3px 14px #1720330c;
    }

    .card h3 {
        margin: 0 0 14px;
        color: #657089;
        font-size: 14px;
    }

    .number {
        font-size: 28px;
        font-weight: bold;
        overflow-wrap: anywhere;
    }

    .panel {
        margin-bottom: 24px;
        overflow: hidden;
    }

    .panel h2 { margin-top: 0; }

    .table-wrap { overflow-x: auto; }

    table {
        width: 100%;
        border-collapse: collapse;
        min-width: 600px;
    }

    th, td {
        text-align: left;
        padding: 13px;
        border-bottom: 1px solid #e9edf4;
    }

    th {
        background: #f7f8fc;
        color: #536078;
        font-size: 13px;
    }

    button {
        border: 0;
        border-radius: 8px;
        background: #243b80;
        color: white;
        padding: 11px 16px;
        cursor: pointer;
    }

    button:hover { background: #172a62; }

    #message { margin-bottom: 16px; }

    @media (max-width: 600px) {
        body { padding: 15px; }
    }
</style>
</head>
<body>

<header>
    <div>
        <h1>Dholakpur Admin</h1>
        <p>Database overview and transaction monitoring</p>
    </div>
    <button id="refreshButton" type="button">Refresh data</button>
</header>

<div id="message" role="status">Loading database information...</div>

<section class="cards">
    <div class="card">
        <h3>Total accounts</h3>
        <div class="number" id="totalAccounts">—</div>
    </div>

    <div class="card">
        <h3>Combined account balances</h3>
        <div class="number" id="totalBalance">—</div>
    </div>

    <div class="card">
        <h3>Total transactions</h3>
        <div class="number" id="totalTransactions">—</div>
    </div>
</section>

<section class="panel">
    <h2>Registered accounts</h2>
    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Account number</th>
                    <th>Customer name</th>
                    <th>Balance</th>
                </tr>
            </thead>
            <tbody id="accountsBody"></tbody>
        </table>
    </div>
</section>

<section class="panel">
    <h2>Recent transactions</h2>
    <p>Showing the latest 200 transactions.</p>
    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Transaction ID</th>
                    <th>Account number</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Balance afterward</th>
                    <th>Date and time</th>
                </tr>
            </thead>
            <tbody id="transactionsBody"></tbody>
        </table>
    </div>
</section>

<script>
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function money(value) {
    return "₹" + Number(value).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

async function loadDashboard() {
    const message = document.getElementById("message");
    message.textContent = "Loading database information...";

    try {
        const responses = await Promise.all([
            fetch("/api/admin/summary", { cache: "no-store" }),
            fetch("/api/admin/accounts", { cache: "no-store" }),
            fetch("/api/admin/transactions", { cache: "no-store" })
        ]);

        if (responses.some(response => response.status === 401)) {
            message.textContent =
                "Admin authentication failed. Reload the page and sign in again.";
            return;
        }

        if (responses.some(response => !response.ok)) {
            throw new Error(
                "Could not load the database information. Check admin credentials."
            );
        }

        const [summary, accountsData, transactionsData] =
            await Promise.all(responses.map(response => response.json()));

        document.getElementById("totalAccounts").textContent =
            summary.total_accounts;

        document.getElementById("totalBalance").textContent =
            money(summary.total_balance);

        document.getElementById("totalTransactions").textContent =
            summary.total_transactions;

        document.getElementById("accountsBody").innerHTML =
            accountsData.accounts.map(account => `
                <tr>
                    <td>${escapeHTML(account.account_number)}</td>
                    <td>${escapeHTML(account.name)}</td>
                    <td>${money(account.balance)}</td>
                </tr>
            `).join("") ||
            '<tr><td colspan="3">No accounts found.</td></tr>';

        document.getElementById("transactionsBody").innerHTML =
            transactionsData.transactions.map(transaction => `
                <tr>
                    <td>${escapeHTML(transaction.transaction_id)}</td>
                    <td>${escapeHTML(transaction.account_number)}</td>
                    <td>${escapeHTML(transaction.transaction_type)}</td>
                    <td>${money(transaction.amount)}</td>
                    <td>${money(transaction.balance_after)}</td>
                    <td>${escapeHTML(transaction.created_at)}</td>
                </tr>
            `).join("") ||
            '<tr><td colspan="6">No transactions found.</td></tr>';

        message.textContent =
            "Database information loaded successfully.";

    } catch (error) {
        message.textContent = error.message;
    }
}

document.getElementById("refreshButton").addEventListener(
    "click",
    loadDashboard
);

loadDashboard();
</script>

</body>
</html>
""")

    response.headers["Cache-Control"] = "no-store"
    return response


# =========================================================
# ADMIN API: SUMMARY
# =========================================================

@app.get("/api/admin/summary")
def admin_summary(
    admin: str = Depends(require_admin),
):
    connection = get_connection()

    try:
        account_summary = connection.execute("""
            SELECT COUNT(*) AS total_accounts,
                   COALESCE(SUM(balance), 0) AS total_balance
            FROM accounts
        """).fetchone()

        transaction_summary = connection.execute("""
            SELECT COUNT(*) AS total_transactions
            FROM transactions
        """).fetchone()

        return {
            "total_accounts": account_summary["total_accounts"],
            "total_balance": account_summary["total_balance"],
            "total_transactions": transaction_summary["total_transactions"],
        }

    finally:
        connection.close()


# =========================================================
# ADMIN API: ACCOUNT LIST
# Never return PINs or PIN hashes.
# =========================================================

@app.get("/api/admin/accounts")
def admin_accounts(
    admin: str = Depends(require_admin),
):
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT account_number, name, balance
            FROM accounts
            ORDER BY account_number
        """).fetchall()

        return {
            "accounts": [dict(row) for row in rows]
        }

    finally:
        connection.close()


# =========================================================
# ADMIN API: RECENT TRANSACTIONS
# =========================================================

@app.get("/api/admin/transactions")
def admin_transactions(
    admin: str = Depends(require_admin),
):
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT transaction_id,
                   account_number,
                   transaction_type,
                   amount,
                   balance_after,
                   created_at
            FROM transactions
            ORDER BY transaction_id DESC
            LIMIT 200
        """).fetchall()

        return {
            "transactions": [dict(row) for row in rows]
        }

    finally:
        connection.close()
