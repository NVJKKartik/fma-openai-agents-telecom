"""Tool definitions (names, descriptions, argument schemas) exposed to the agents."""

import json
from typing import Literal

from agents import function_tool

import logic


def _out(result: dict) -> str:
    return json.dumps(result)


@function_tool
def verify_account(last4: str, zip_code: str) -> str:
    """Verify a customer's identity. Returns the account number when the details match.

    Args:
        last4: Last 4 digits of the customer's account number.
        zip_code: Billing ZIP code on the account.
    """
    return _out(logic.verify_account(last4, zip_code))


@function_tool
def get_bill(account_number: str) -> str:
    """Get the current bill: every charge, the total due, the due date and credits applied.

    Args:
        account_number: Full account number, as returned by verify_account.
    """
    return _out(logic.get_bill(account_number))


@function_tool
def explain_charge(account_number: str, charge_id: str) -> str:
    """Explain a single line on the current bill.

    Args:
        account_number: Full account number, as returned by verify_account.
        charge_id: Charge id from get_bill, for example C3.
    """
    return _out(logic.explain_charge(account_number, charge_id))


@function_tool
def apply_credit(account_number: str, amount: float, reason: Literal["outage", "billing_error", "goodwill"]) -> str:
    """Apply a bill credit to the account. Credits are capped per reason by policy.

    Args:
        account_number: Full account number, as returned by verify_account.
        amount: Credit amount in US dollars.
        reason: Why the credit is given.
    """
    return _out(logic.apply_credit(account_number, amount, reason))


@function_tool
def check_outage(zip_code: str) -> str:
    """List known network outages for a ZIP code.

    Args:
        zip_code: 5-digit ZIP code.
    """
    return _out(logic.check_outage(zip_code))


@function_tool
def run_line_diagnostic(account_number: str, phone_number: str) -> str:
    """Run a remote diagnostic on one line: status, signal strength and common faults.

    Args:
        account_number: Full account number, as returned by verify_account.
        phone_number: The line's phone number, formatted like 415-555-0134.
    """
    return _out(logic.run_line_diagnostic(account_number, phone_number))


@function_tool
def change_plan(account_number: str, new_plan: Literal["basic", "plus", "premium"], confirm: bool) -> str:
    """Preview or apply a plan change. With confirm=false nothing changes and the terms are returned.

    Args:
        account_number: Full account number, as returned by verify_account.
        new_plan: The plan to move to.
        confirm: True to apply the change, false to preview the terms.
    """
    return _out(logic.change_plan(account_number, new_plan, confirm))


@function_tool
def schedule_technician(account_number: str, visit_date: str, window: Literal["morning", "afternoon"]) -> str:
    """Book an on-site technician visit.

    Args:
        account_number: Full account number, as returned by verify_account.
        visit_date: Visit date in DD/MM/YYYY format. Must be tomorrow or within 14 days; no Sundays.
        window: Arrival window: morning (8-12) or afternoon (12-17).
    """
    return _out(logic.schedule_technician(account_number, visit_date, window))
