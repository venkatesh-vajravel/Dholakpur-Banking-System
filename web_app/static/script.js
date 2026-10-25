
let currentAccount = null;
let verifiedPinAccount = null;


// ==========================================
// PAGE CONTROL
// ==========================================

function hideAllPages() {

    document
        .getElementById("homePage")
        .classList.add("hidden");

    document
        .getElementById("createAccountPage")
        .classList.add("hidden");

    document
        .getElementById("loginPage")
        .classList.add("hidden");

    document
        .getElementById("dashboardPage")
        .classList.add("hidden");
}


function showHome() {

    hideAllPages();

    document
        .getElementById("homePage")
        .classList.remove("hidden");
}


function showCreateAccount() {

    hideAllPages();

    document
        .getElementById("createAccountPage")
        .classList.remove("hidden");
}


function showLogin() {

    hideAllPages();

    document
        .getElementById("loginPage")
        .classList.remove("hidden");
}


function showAbout() {

    alert(
        "Dholakpur Banking System\n\n" +
        "Built using Python, FastAPI, HTML, CSS and JavaScript."
    );
}


// ==========================================
// MESSAGE
// ==========================================

function showMessage(elementId, message, success) {

    const element =
        document.getElementById(elementId);

    element.textContent = message;

    element.className =
        "message " + (success ? "success" : "error");
}


// ==========================================
// CREATE ACCOUNT
// ==========================================

document
    .getElementById("createAccountForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const accountNumber =
            document
                .getElementById("createAccountNumber")
                .value;

        const name =
            document
                .getElementById("createName")
                .value;

        const pin =
            document
                .getElementById("createPin")
                .value;

        const formData = new FormData();

        formData.append("account_number", accountNumber);
        formData.append("name", name);
        formData.append("pin", pin);

        try {

            const response = await fetch(
                "/api/create-account",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            showMessage(
                "createMessage",
                data.message,
                data.success
            );

            if (data.success) {

                document
                    .getElementById("createAccountForm")
                    .reset();

            }

        } catch (error) {

            showMessage(
                "createMessage",
                "Unable to create account. Please try again.",
                false
            );

        }

    });


// ==========================================
// LOGIN
// ==========================================

document
    .getElementById("loginForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const accountNumber =
            document
                .getElementById("loginAccountNumber")
                .value;

        const pin =
            document
                .getElementById("loginPin")
                .value;

        const formData = new FormData();

        formData.append("account_number", accountNumber);
        formData.append("pin", pin);

        try {

            const response = await fetch(
                "/api/login",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            showMessage(
                "loginMessage",
                data.message,
                data.success
            );

            if (data.success) {

                currentAccount = {
                    accountNumber: data.account_number,
                    name: data.name,
                    balance: data.balance,
                    pin: pin
                };

                openDashboard();

            }

        } catch (error) {

            showMessage(
                "loginMessage",
                "Unable to log in. Please try again.",
                false
            );

        }

    });


// ==========================================
// DASHBOARD
// ==========================================

function openDashboard() {

    hideAllPages();

    document
        .getElementById("dashboardPage")
        .classList.remove("hidden");

    document
        .getElementById("dashboardName")
        .textContent = currentAccount.name;

    document
        .getElementById("dashboardAccount")
        .textContent = currentAccount.accountNumber;

    updateBalance();
}


function updateBalance() {

    document
        .getElementById("balanceAmount")
        .textContent =
        Number(currentAccount.balance).toFixed(2);
}


// ==========================================
// DASHBOARD BOXES
// ==========================================

function hideDashboardForms() {

    document
        .getElementById("depositBox")
        .classList.add("hidden");

    document
        .getElementById("withdrawBox")
        .classList.add("hidden");

    document
        .getElementById("changePinBox")
        .classList.add("hidden");
}


function showBalance() {

    hideDashboardForms();

    showMessage(
        "dashboardMessage",
        "Your current balance is ₹" +
        Number(currentAccount.balance).toFixed(2),
        true
    );
}


function showDeposit() {

    hideDashboardForms();

    document
        .getElementById("depositBox")
        .classList.remove("hidden");
}


function showWithdraw() {

    hideDashboardForms();

    document
        .getElementById("withdrawBox")
        .classList.remove("hidden");
}


function showDetails() {

    hideDashboardForms();

    showMessage(
        "dashboardMessage",

        "Account Number: " +
        currentAccount.accountNumber +
        " | Name: " +
        currentAccount.name +
        " | Balance: ₹" +
        Number(currentAccount.balance).toFixed(2),

        true
    );
}


function showChangePin() {

    hideDashboardForms();

    resetPinVerification();

    document
        .getElementById("verifyPinAccountForm")
        .reset();

    document
        .getElementById("verifyPinMessage")
        .textContent = "";

    document
        .getElementById("dashboardMessage")
        .textContent = "";

    document
        .getElementById("changePinBox")
        .classList.remove("hidden");
}


// ==========================================
// DEPOSIT
// ==========================================

document
    .getElementById("depositForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const amount =
            document
                .getElementById("depositAmount")
                .value;

        const formData = new FormData();

        formData.append(
            "account_number",
            currentAccount.accountNumber
        );

        formData.append("pin", currentAccount.pin);
        formData.append("amount", amount);

        try {

            const response = await fetch(
                "/api/deposit",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            showMessage(
                "dashboardMessage",
                data.message,
                data.success
            );

            if (data.success) {

                currentAccount.balance = data.balance;

                updateBalance();

                document
                    .getElementById("depositForm")
                    .reset();

            }

        } catch (error) {

            showMessage(
                "dashboardMessage",
                "Unable to complete deposit. Please try again.",
                false
            );

        }

    });


// ==========================================
// WITHDRAW
// ==========================================

document
    .getElementById("withdrawForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const amount =
            document
                .getElementById("withdrawAmount")
                .value;

        const formData = new FormData();

        formData.append(
            "account_number",
            currentAccount.accountNumber
        );

        formData.append("pin", currentAccount.pin);
        formData.append("amount", amount);

        try {

            const response = await fetch(
                "/api/withdraw",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            showMessage(
                "dashboardMessage",
                data.message,
                data.success
            );

            if (data.success) {

                currentAccount.balance = data.balance;

                updateBalance();

                document
                    .getElementById("withdrawForm")
                    .reset();

            }

        } catch (error) {

            showMessage(
                "dashboardMessage",
                "Unable to complete withdrawal. Please try again.",
                false
            );

        }

    });


// ==========================================
// CHANGE PIN - RESET VERIFICATION
// ==========================================

function resetPinVerification() {

    verifiedPinAccount = null;

    document
        .getElementById("newPinSection")
        .classList.add("hidden");

    document
        .getElementById("changePinForm")
        .reset();
}


// Changing either detail invalidates the local token.

document
    .getElementById("changePinAccountNumber")
    .addEventListener("input", resetPinVerification);

document
    .getElementById("changePinName")
    .addEventListener("input", resetPinVerification);


// ==========================================
// CHANGE PIN - STEP 1: VERIFY ACCOUNT
// ==========================================

document
    .getElementById("verifyPinAccountForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        // Invalidate any previously received token locally.
        resetPinVerification();

        const accountNumber =
            document
                .getElementById("changePinAccountNumber")
                .value.trim();

        const name =
            document
                .getElementById("changePinName")
                .value.trim();

        const formData = new FormData();

        formData.append("account_number", accountNumber);
        formData.append("name", name);

        try {

            const response = await fetch(
                "/api/verify-pin-account",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {

                showMessage(
                    "verifyPinMessage",
                    data.message || "Account verification failed.",
                    false
                );

                return;

            }

            // Store the server-issued token for this operation.
            verifiedPinAccount = {
                accountNumber: data.account_number,
                name: data.name,
                token: data.verification_token
            };

            showMessage(
                "verifyPinMessage",
                data.message,
                true
            );

            document
                .getElementById("newPinSection")
                .classList.remove("hidden");

        } catch (error) {

            resetPinVerification();

            showMessage(
                "verifyPinMessage",
                "Unable to verify account. Please try again.",
                false
            );

        }

    });


// ==========================================
// CHANGE PIN - STEP 2: SET NEW PIN
// ==========================================

document
    .getElementById("changePinForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        if (!verifiedPinAccount) {

            showMessage(
                "verifyPinMessage",
                "Please verify the account first.",
                false
            );

            return;

        }

        const newPin =
            document
                .getElementById("newPin")
                .value;

        if (!/^\d{4}$/.test(newPin)) {

            showMessage(
                "dashboardMessage",
                "PIN must contain exactly 4 digits!",
                false
            );

            return;

        }

        const formData = new FormData();

        formData.append(
            "verification_token",
            verifiedPinAccount.token
        );

        formData.append("new_pin", newPin);

        // Capture the current token and immediately invalidate
        // local verification to prevent accidental resubmission.
        const tokenAccountNumber =
            verifiedPinAccount.accountNumber;

        verifiedPinAccount = null;

        document
            .getElementById("newPinSection")
            .classList.add("hidden");

        try {

            const response = await fetch(
                "/api/change-pin",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            showMessage(
                "dashboardMessage",
                data.message ||
                    "Unable to change PIN. Please verify again.",
                response.ok && data.success
            );

            if (response.ok && data.success) {

                // Update the local PIN only when this is
                // the account currently logged in.

                if (
                    currentAccount &&
                    currentAccount.accountNumber ===
                    tokenAccountNumber
                ) {

                    currentAccount.pin = newPin;

                }

                document
                    .getElementById("verifyPinAccountForm")
                    .reset();

                document
                    .getElementById("changePinForm")
                    .reset();

                document
                    .getElementById("verifyPinMessage")
                    .textContent = "";

            } else {

                showMessage(
                    "verifyPinMessage",
                    "Verification was consumed or failed. Verify your account again before retrying.",
                    false
                );

            }

        } catch (error) {

            showMessage(
                "dashboardMessage",
                "Unable to change PIN. Verify your account again before retrying.",
                false
            );

        }

    });


// ==========================================
// LOGOUT
// ==========================================

function logout() {

    currentAccount = null;

    verifiedPinAccount = null;

    document
        .getElementById("loginForm")
        .reset();

    resetPinVerification();

    showHome();
}
