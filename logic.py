"""Business rules for accounts, bills, credits, plans, outages and technician visits."""

from datetime import date, datetime, timedelta

import config
from data import ACCOUNTS, CREDIT_CAPS, OUTAGES, PLANS

CYCLE_DAYS = 30
ETF_PER_MONTH = 10.00
ETF_MAX = 100.00
_visits: list[dict] = []


def today() -> date:
    return date.fromisoformat(config.TODAY)


def _account(number: str) -> dict | None:
    return ACCOUNTS.get(number.strip())


def _no_account() -> dict:
    return {"ok": False, "error": "no account with that number"}


def _total(acct: dict) -> float:
    return round(sum(c["amount"] for c in acct["charges"]), 2)


def verify_account(last4: str, zip_code: str) -> dict:
    for number, acct in ACCOUNTS.items():
        if number.replace("-", "")[-4:] == last4.strip() and acct["zip"] == zip_code.strip():
            return {"ok": True, "verified": True, "account_number": number, "holder": acct["holder"],
                    "plan": PLANS[acct["plan"]]["name"], "lines": list(acct["lines"])}
    return {"ok": False, "verified": False, "error": "the details do not match an account"}


def get_bill(account_number: str) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    return {"ok": True, "holder": acct["holder"], "charges": acct["charges"], "total_due": _total(acct),
            "due_date": acct["due_date"], "credits_applied": acct["credits"]}


def explain_charge(account_number: str, charge_id: str) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    for charge in acct["charges"]:
        if charge["id"] == charge_id.strip().upper():
            return {"ok": True, "charge": charge}
    return {"ok": False, "error": "no charge with that id on the current bill"}


def apply_credit(account_number: str, amount: float, reason: str) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    if reason not in ("outage", "billing_error", "goodwill"):
        return {"ok": False, "error": "reason must be outage, billing_error or goodwill"}
    if amount <= 0:
        return {"ok": False, "error": "amount must be positive"}
    cap = CREDIT_CAPS.get(reason)
    if cap is not None and amount > cap:
        return {"ok": False, "error": f"credits for {reason} are capped at ${cap:.2f}"}
    acct["credits"].append({"amount": round(amount, 2), "reason": reason, "date": config.TODAY})
    acct["charges"].append({"id": f"K{len(acct['credits'])}", "desc": f"Credit ({reason})", "amount": -round(amount, 2)})
    return {"ok": True, "credited": round(amount, 2), "new_total_due": _total(acct)}


def check_outage(zip_code: str) -> dict:
    z = zip_code.strip()
    found = [o for o in OUTAGES if o["zip"][:3] == z[:3]]
    return {"ok": True, "zip": z, "outages": found}


def run_line_diagnostic(account_number: str, phone_number: str) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    line = acct["lines"].get(phone_number.strip())
    if line is None:
        return {"ok": False, "error": "that number is not a line on this account"}
    if line["status"] != "active":
        return {"ok": True, "status": line["status"], "finding": "line is suspended; service is off until reactivated"}
    findings = []
    if line["signal_dbm"] < -105:
        findings.append("weak signal at the customer's location")
    if line["last_reboot_days"] > 30:
        findings.append("device has not been restarted in over 30 days")
    return {"ok": True, "status": "active", "signal_dbm": line["signal_dbm"],
            "findings": findings or ["no problems found"]}


def preview_plan_change(acct: dict, new_plan: str) -> dict:
    old, new = PLANS[acct["plan"]], PLANS[new_plan]
    days_left = (date.fromisoformat(acct["cycle_end"]) - today()).days
    diff = new["price"] - old["price"]
    if diff > 0:
        elapsed = CYCLE_DAYS - days_left
        prorated = round(diff * elapsed / CYCLE_DAYS, 2)
        return {"direction": "upgrade", "effective": "immediately", "prorated_charge_today": prorated,
                "early_termination_fee": 0.0}
    etf = min(ETF_MAX, ETF_PER_MONTH * acct["contract_months_left"])
    return {"direction": "downgrade", "effective": acct["cycle_end"], "prorated_charge_today": 0.0,
            "early_termination_fee": etf}


def change_plan(account_number: str, new_plan: str, confirm: bool) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    if new_plan not in PLANS:
        return {"ok": False, "error": "new_plan must be basic, plus or premium"}
    if new_plan == acct["plan"]:
        return {"ok": False, "error": "the account is already on that plan"}
    terms = preview_plan_change(acct, new_plan)
    if not confirm:
        return {"ok": True, "applied": False, "preview": terms, "new_monthly_price": PLANS[new_plan]["price"]}
    fees = terms["prorated_charge_today"] + terms["early_termination_fee"]
    if fees:
        acct["charges"].append({"id": "P1", "desc": "Plan change fees", "amount": round(fees, 2)})
    acct["plan"] = new_plan
    return {"ok": True, "applied": True, "terms": terms, "new_monthly_price": PLANS[new_plan]["price"]}


def schedule_technician(account_number: str, visit_date: str, window: str) -> dict:
    acct = _account(account_number)
    if acct is None:
        return _no_account()
    try:
        day = datetime.strptime(visit_date.strip(), "%m/%d/%Y").date()
    except ValueError:
        return {"ok": False, "error": "invalid date"}
    if window not in ("morning", "afternoon"):
        return {"ok": False, "error": "window must be morning or afternoon"}
    if not today() < day <= today() + timedelta(days=14):
        return {"ok": False, "error": "visits can be booked from tomorrow up to 14 days ahead"}
    if day.weekday() == 6:
        return {"ok": False, "error": "no visits on Sunday"}
    if any(v["date"] == day.isoformat() and v["window"] == window for v in _visits):
        return {"ok": False, "error": "that window is full"}
    visit = {"id": f"TECH-{len(_visits) + 1:03d}", "account": account_number, "date": day.isoformat(), "window": window}
    _visits.append(visit)
    return {"ok": True, "visit": visit}
