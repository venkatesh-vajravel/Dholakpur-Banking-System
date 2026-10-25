
import os
import sqlite3
import hashlib
import secrets
import math


# Always use the database in the main project folder.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(PROJECT_ROOT, "dholakpur.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pin TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0
                    CHECK (balance >= 0)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('deposit', 'withdraw')),
                amount REAL NOT NULL CHECK (amount > 0),
                balance_after REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number)
                    REFERENCES accounts(account_number)
            )
        """)

        connection.commit()

    finally:
        connection.close()


def hash_pin(pin):
    salt = secrets.token_hex(16)

    pin_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt.encode("utf-8"),
        600000
    )

    return salt + ":" + pin_hash.hex()


def verify_hashed_pin(pin, stored_hash):
    try:
        salt, saved_hash = stored_hash.split(":", 1)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            salt.encode("utf-8"),
            600000
        )

        return secrets.compare_digest(
            calculated_hash.hex(),
            saved_hash
        )

    except (ValueError, TypeError):
        return False


def create_account(account_number, name, pin):
    if len(pin) != 4 or not pin.isdigit():
        return False

    hashed_pin = hash_pin(pin)
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO accounts
                (account_number, name, pin, balance)
            VALUES (?, ?, ?, 0)
            """,
            (account_number, name, hashed_pin)
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        connection.rollback()
        return False

    finally:
        connection.close()


def get_account(account_number):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT account_number, name, pin, balance
            FROM accounts
            WHERE account_number = ?
            """,
            (account_number,)
        ).fetchone()

        return dict(row) if row is not None else None

    finally:
        connection.close()


def verify_account_pin(account_number, pin):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT pin FROM accounts WHERE account_number = ?",
            (account_number,)
        ).fetchone()

        if row is None:
            return False

        stored_pin = row["pin"]

        # Migrate an existing plain-text PIN after successful verification.
        if ":" not in stored_pin:
            if not secrets.compare_digest(stored_pin, pin):
                return False

            connection.execute(
                "UPDATE accounts SET pin = ? WHERE account_number = ?",
                (hash_pin(pin), account_number)
            )
            connection.commit()
            return True

        return verify_hashed_pin(pin, stored_pin)

    finally:
        connection.close()


def change_account_pin(account_number, new_pin):
    if len(new_pin) != 4 or not new_pin.isdigit():
        return False

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE accounts
            SET pin = ?
            WHERE account_number = ?
            """,
            (hash_pin(new_pin), account_number)
        )

        connection.commit()
        return cursor.rowcount == 1

    finally:
        connection.close()


def apply_transaction(account_number, transaction_type, amount):
    if transaction_type not in ("deposit", "withdraw"):
        return "invalid_type", None

    if not math.isfinite(amount) or amount <= 0:
        return "invalid_amount", None

    connection = get_connection()

    try:
        # Prevent concurrent transactions from overwriting balances.
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute(
            """
            SELECT balance
            FROM accounts
            WHERE account_number = ?
            """,
            (account_number,)
        ).fetchone()

        if row is None:
            connection.rollback()
            return "account_not_found", None

        current_balance = row["balance"]

        if transaction_type == "withdraw":
            if amount > current_balance:
                connection.rollback()
                return "insufficient_balance", current_balance

            new_balance = current_balance - amount

        else:
            new_balance = current_balance + amount

        connection.execute(
            """
            UPDATE accounts
            SET balance = ?
            WHERE account_number = ?
            """,
            (new_balance, account_number)
        )

        connection.execute(
            """
            INSERT INTO transactions
                (account_number, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
            """,
            (account_number, transaction_type, amount, new_balance)
        )

        connection.commit()
        return "success", new_balance

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_transactions(account_number):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT transaction_id, transaction_type, amount,
                   balance_after, created_at
            FROM transactions
            WHERE account_number = ?
            ORDER BY transaction_id DESC
            """,
            (account_number,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    print("Dholakpur database initialized successfully!")
    print("Database location:", DATABASE_NAME)
