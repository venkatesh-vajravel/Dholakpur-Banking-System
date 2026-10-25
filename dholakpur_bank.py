# ==========================================
#       DHOLAKPUR BANKING SYSTEM
# ==========================================

accounts = {}


def create_account():

    print("\n===== CREATE NEW ACCOUNT =====")

    account_number = input("Enter account number: ")

    if account_number in accounts:
        print("Account already exists!")
        return

    name = input("Enter your name: ")

    while True:
        pin = input("Set your secret 4-digit PIN: ")

        if len(pin) == 4 and pin.isdigit():
            break

        print("PIN must contain exactly 4 digits!")

    accounts[account_number] = {
        "name": name,
        "pin": pin,
        "balance": 0
    }

    print("\nAccount created successfully!")
    print(f"Welcome to Dholakpur Banking, {name}!")


def check_balance():

    print("\n===== CHECK BALANCE =====")

    account_number = input("Enter your account number: ")

    if account_number not in accounts:
        print("Account not found!")
        return

    pin = input("Enter your secret PIN: ")

    if pin != accounts[account_number]["pin"]:
        print("Incorrect PIN!")
        return

    print(f"\nAccount Name: {accounts[account_number]['name']}")
    print(f"Your balance is: ₹{accounts[account_number]['balance']:.2f}")


def deposit():

    print("\n===== DEPOSIT MONEY =====")

    account_number = input("Enter your account number: ")

    if account_number not in accounts:
        print("Account not found!")
        return

    pin = input("Enter your secret PIN: ")

    if pin != accounts[account_number]["pin"]:
        print("Incorrect PIN!")
        return

    amount = float(input("Enter amount to deposit: ₹"))

    if amount <= 0:
        print("Invalid amount!")
        return

    accounts[account_number]["balance"] += amount

    print("\nDeposit successful!")
    print(f"Amount deposited: ₹{amount:.2f}")
    print(
        f"New balance: ₹"
        f"{accounts[account_number]['balance']:.2f}"
    )


def withdraw():

    print("\n===== WITHDRAW MONEY =====")

    account_number = input("Enter your account number: ")

    if account_number not in accounts:
        print("Account not found!")
        return

    pin = input("Enter your secret PIN: ")

    if pin != accounts[account_number]["pin"]:
        print("Incorrect PIN!")
        return

    amount = float(input("Enter amount to withdraw: ₹"))

    if amount <= 0:
        print("Invalid amount!")
        return

    if amount > accounts[account_number]["balance"]:
        print("Insufficient balance!")
        return

    accounts[account_number]["balance"] -= amount

    print("\nWithdrawal successful!")
    print(f"Amount withdrawn: ₹{amount:.2f}")
    print(
        f"New balance: ₹"
        f"{accounts[account_number]['balance']:.2f}"
    )


def change_pin():

    print("\n===== CHANGE / FORGOT PIN =====")

    account_number = input("Enter your account number: ")

    if account_number not in accounts:
        print("Account not found!")
        return

    name = input("Enter your account name: ")

    if name.lower() != accounts[account_number]["name"].lower():
        print("Account name does not match!")
        return

    print("\nAccount verified!")

    while True:

        new_pin = input("Enter your new 4-digit PIN: ")

        if len(new_pin) == 4 and new_pin.isdigit():
            break

        print("PIN must contain exactly 4 digits!")

    accounts[account_number]["pin"] = new_pin

    print("Your PIN has been changed successfully!")


def account_details():

    print("\n===== ACCOUNT DETAILS =====")

    account_number = input("Enter your account number: ")

    if account_number not in accounts:
        print("Account not found!")
        return

    pin = input("Enter your secret PIN: ")

    if pin != accounts[account_number]["pin"]:
        print("Incorrect PIN!")
        return

    account = accounts[account_number]

    print("\n----- YOUR DETAILS -----")
    print(f"Account Number : {account_number}")
    print(f"Account Name   : {account['name']}")
    print(f"Balance        : ₹{account['balance']:.2f}")

if __name__ == "__main__":
    while True:
        print("\n================================")
        print("     WELCOME TO DHOLAKPUR")
        print("          BANKING")
        print("================================")

        print("1. Create New Account")
        print("2. Check Balance")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Change / Forgot PIN")
        print("6. Account Details")
        print("7. Exit")

        choice = input("\nEnter your choice: ")

        match choice:
            case "1":
                create_account()

            case "2":
                check_balance()
            case "3":
                deposit()
            case "4":
                withdraw()
            case "5":
                change_pin()
            case "6":
                account_details()
            case "7":
                print("\nThank you for using Dholakpur Banking!")
                break
            case _:
                print("Invalid choice!")