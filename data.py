"""Seeded customer accounts, plans and network outages."""

PLANS = {
    "basic": {"name": "Basic", "price": 30.00, "data": "5 GB"},
    "plus": {"name": "Plus", "price": 50.00, "data": "50 GB"},
    "premium": {"name": "Premium", "price": 75.00, "data": "Unlimited"},
}

# Days left in the current billing cycle are measured from TODAY to cycle_end.
ACCOUNTS = {
    "4410-2287-0931": {
        "holder": "Maria Alvarez",
        "zip": "94110",
        "plan": "plus",
        "contract_months_left": 8,
        "cycle_end": "2026-11-30",
        "due_date": "2026-11-25",
        "lines": {
            "415-555-0134": {"label": "Maria", "status": "active", "signal_dbm": -78, "last_reboot_days": 3},
            "415-555-0177": {"label": "Carlos", "status": "active", "signal_dbm": -112, "last_reboot_days": 40},
        },
        "charges": [
            {"id": "C1", "desc": "Plus plan", "amount": 50.00},
            {"id": "C2", "desc": "Additional line 415-555-0177", "amount": 20.00},
            {"id": "C3", "desc": "Device installment 7 of 24", "amount": 12.60},
            {"id": "C4", "desc": "International roaming (Mexico, 3 days)", "amount": 15.00},
            {"id": "C5", "desc": "Taxes and fees", "amount": 7.40},
        ],
        "credits": [],
    },
    "7733-1048-5526": {
        "holder": "Devon Park",
        "zip": "60614",
        "plan": "basic",
        "contract_months_left": 0,
        "cycle_end": "2026-11-20",
        "due_date": "2026-11-18",
        "lines": {
            "312-555-0190": {"label": "Devon", "status": "active", "signal_dbm": -85, "last_reboot_days": 12},
        },
        "charges": [
            {"id": "C1", "desc": "Basic plan", "amount": 30.00},
            {"id": "C2", "desc": "Taxes and fees", "amount": 4.50},
        ],
        "credits": [],
    },
    "2209-8841-3370": {
        "holder": "Priya Nair",
        "zip": "10027",
        "plan": "premium",
        "contract_months_left": 2,
        "cycle_end": "2026-11-15",
        "due_date": "2026-11-12",
        "lines": {
            "212-555-0111": {"label": "Priya", "status": "active", "signal_dbm": -70, "last_reboot_days": 5},
            "212-555-0112": {"label": "Anil", "status": "active", "signal_dbm": -74, "last_reboot_days": 9},
            "212-555-0113": {"label": "Meera", "status": "suspended", "signal_dbm": None, "last_reboot_days": 60},
        },
        "charges": [
            {"id": "C1", "desc": "Premium plan", "amount": 75.00},
            {"id": "C2", "desc": "Additional lines (2)", "amount": 50.00},
            {"id": "C3", "desc": "Device installment 3 of 24", "amount": 59.99},
            {"id": "C4", "desc": "Device installment 3 of 24", "amount": 59.99},
            {"id": "C5", "desc": "Taxes and fees", "amount": 18.00},
        ],
        "credits": [],
    },
    "5086-6612-1175": {
        "holder": "Tom Becker",
        "zip": "73301",
        "plan": "plus",
        "contract_months_left": 0,
        "cycle_end": "2026-12-02",
        "due_date": "2026-12-01",
        "lines": {
            "512-555-0142": {"label": "Tom", "status": "active", "signal_dbm": -101, "last_reboot_days": 30},
        },
        "charges": [
            {"id": "C1", "desc": "Plus plan", "amount": 50.00},
            {"id": "C2", "desc": "Taxes and fees", "amount": 6.50},
            {"id": "C3", "desc": "Autopay discount", "amount": -5.00},
            {"id": "C4", "desc": "Payment received", "amount": -51.50},
        ],
        "credits": [{"amount": 10.00, "reason": "goodwill", "date": "2026-10-02"}],
    },
}

OUTAGES = [
    {"id": "OUT-3301", "zip": "94110", "area": "Mission District, San Francisco", "started": "2026-11-08",
     "est_restore": "2026-11-11", "affects": "voice and data"},
    {"id": "OUT-3315", "zip": "60618", "area": "Avondale, Chicago", "started": "2026-11-09",
     "est_restore": "2026-11-10", "affects": "data only"},
    {"id": "OUT-3320", "zip": "10031", "area": "Hamilton Heights, New York", "started": "2026-11-10",
     "est_restore": "2026-11-12", "affects": "voice and data"},
]

CREDIT_CAPS = {"outage": 25.00, "billing_adjustment": 50.00, "goodwill": 10.00}
