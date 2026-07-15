"""Generates synthetic sample data with the same schema as the real
daily_expenses / budget_settings / user_cards / fixed_expenses tables,
for a public-safe Power BI portfolio demo. All values are fictional."""
import csv
import random
import datetime

random.seed(42)

OUT_DIR = r"C:\Users\sunny\personal-finance-dashboard-portfolio\data"

CURRENCIES = ["EUR", "CAD", "TWD", "USD", "JPY"]
CURRENCY_WEIGHTS = [55, 15, 15, 12, 3]

PAYMENT_METHODS = ["Primary Credit Card", "Travel Debit Card", "Digital Wallet", "Cash/Other"]
PAYMENT_WEIGHTS = [45, 20, 20, 15]

# category -> (raw label pool incl. a few intentionally messy variants, item pool, amount range)
CATEGORY_SPEC = {
    "Food": {
        "raw_labels": ["飲食", "Food", "飲食", "Food"],
        "items": ["Groceries", "Coffee", "Lunch", "Dinner", "Bubble tea", "Bakery", "Restaurant", "Snacks"],
        "range": (3, 45),
    },
    "Shopping": {
        "raw_labels": ["購物", "Shopping", "購物", "Shopping"],
        "items": ["Clothing", "Electronics", "Books", "Gift", "Household items", "Shoes"],
        "range": (10, 120),
    },
    "Transport": {
        "raw_labels": ["交通", "Transport", "交通", "Transport"],
        "items": ["Bus pass", "Taxi", "Train ticket", "Bike rental", "Parking", "Fuel"],
        "range": (3, 60),
    },
    "Living": {
        "raw_labels": ["生活", "Living", "生活", "Living", "生活 Living"],
        "items": ["Rent", "Utilities", "Phone bill", "Internet", "Cleaning supplies", "Home repair"],
        "range": (15, 700),
    },
    "Entertainment": {
        "raw_labels": ["娛樂", "Entertainment", "娛樂", "Entertainment"],
        "items": ["Movie tickets", "Concert", "Streaming subscription", "Video game", "Museum entry"],
        "range": (8, 90),
    },
    "Investment": {
        "raw_labels": ["投資", "Investment"],
        "items": ["Stock purchase", "ETF contribution", "Brokerage fee"],
        "range": (50, 400),
    },
    "Learning": {
        "raw_labels": ["學習", "Learning", "學習"],
        "items": ["Online course", "Textbook", "Software subscription", "Workshop fee", "Language app"],
        "range": (10, 120),
    },
}

INCOME_ITEMS = ["Salary", "Freelance payment", "Refund", "Gift received"]
TRANSFER_ITEMS = ["Currency exchange"]

start_date = datetime.date(2026, 2, 1)
end_date = datetime.date(2026, 7, 10)
total_days = (end_date - start_date).days

rows = []
seq_by_mmdd = {}
row_id = 500001


def next_display_id(d):
    mmdd = d.strftime("%m%d")
    seq_by_mmdd[mmdd] = seq_by_mmdd.get(mmdd, 0) + 1
    return f"{mmdd}{seq_by_mmdd[mmdd]:02d}"


def pick_currency():
    return random.choices(CURRENCIES, weights=CURRENCY_WEIGHTS, k=1)[0]


def pick_payment():
    return random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0]


# --- regular day-to-day expenses (weighted toward Food/Living/Shopping) ---
num_expenses = 190
cat_names = list(CATEGORY_SPEC.keys())
cat_weights = [30, 18, 14, 16, 12, 5, 5]

for _ in range(num_expenses):
    d = start_date + datetime.timedelta(days=random.randint(0, total_days))
    cat = random.choices(cat_names, weights=cat_weights, k=1)[0]
    spec = CATEGORY_SPEC[cat]
    label = random.choice(spec["raw_labels"])
    item = random.choice(spec["items"])
    lo, hi = spec["range"]
    amount = round(random.uniform(lo, hi), 2)
    currency = pick_currency()
    payment = pick_payment()
    created = datetime.datetime.combine(d, datetime.time(random.randint(7, 22), random.randint(0, 59)))
    rows.append({
        "id": row_id,
        "display_id": next_display_id(d),
        "transaction_date": d.isoformat(),
        "item_description": item,
        "category": label,
        "amount_original": amount,
        "currency": currency,
        "amount_base": amount,
        "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        "payment_method": payment,
        "location": "",
    })
    row_id += 1

# --- monthly income (roughly once a month, mostly EUR) ---
for month_offset in range(6):
    d = (start_date.replace(day=1) + datetime.timedelta(days=32 * month_offset)).replace(day=random.randint(1, 5))
    if d > end_date:
        continue
    amount = round(random.uniform(1800, 2400), 2)
    created = datetime.datetime.combine(d, datetime.time(9, 0))
    rows.append({
        "id": row_id,
        "display_id": next_display_id(d),
        "transaction_date": d.isoformat(),
        "item_description": random.choice(INCOME_ITEMS),
        "category": random.choice(["Income", "收入"]),
        "amount_original": amount,
        "currency": "EUR",
        "amount_base": amount,
        "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        "payment_method": "Primary Credit Card",
        "location": "",
    })
    row_id += 1

# --- a few currency exchanges ---
for _ in range(4):
    d = start_date + datetime.timedelta(days=random.randint(0, total_days))
    amount = round(random.uniform(100, 500), 2)
    created = datetime.datetime.combine(d, datetime.time(11, 0))
    rows.append({
        "id": row_id,
        "display_id": next_display_id(d),
        "transaction_date": d.isoformat(),
        "item_description": "Currency exchange",
        "category": random.choice(["Transfer", "轉帳"]),
        "amount_original": amount,
        "currency": pick_currency(),
        "amount_base": amount,
        "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
        "payment_method": "Travel Debit Card",
        "location": "",
    })
    row_id += 1

rows.sort(key=lambda r: r["transaction_date"])

with open(f"{OUT_DIR}/daily_expenses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "display_id", "transaction_date", "item_description", "category",
        "amount_original", "currency", "amount_base", "created_at", "payment_method", "location"
    ])
    writer.writeheader()
    writer.writerows(rows)

with open(f"{OUT_DIR}/budget_settings.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["currency", "budget_amount"])
    writer.writeheader()
    writer.writerows([
        {"currency": "EUR", "budget_amount": 1200},
        {"currency": "CAD", "budget_amount": 2200},
        {"currency": "TWD", "budget_amount": 22000},
        {"currency": "USD", "budget_amount": 300},
    ])

with open(f"{OUT_DIR}/user_cards.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["card_name", "billing_day", "payment_due_day"])
    writer.writeheader()
    writer.writerows([
        {"card_name": "Primary Credit Card", "billing_day": 1, "payment_due_day": 15},
        {"card_name": "Travel Debit Card", "billing_day": "", "payment_due_day": ""},
        {"card_name": "Digital Wallet", "billing_day": "", "payment_due_day": ""},
        {"card_name": "Cash/Other", "billing_day": "", "payment_due_day": ""},
    ])

with open(f"{OUT_DIR}/fixed_expenses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "item_description", "amount", "currency", "category", "payment_method", "charge_day"
    ])
    writer.writeheader()
    writer.writerows([
        {"id": 1, "item_description": "Phone Bill", "amount": 25, "currency": "EUR", "category": "Living", "payment_method": "Primary Credit Card", "charge_day": 5},
        {"id": 2, "item_description": "Streaming Subscription", "amount": 15, "currency": "EUR", "category": "Entertainment", "payment_method": "Digital Wallet", "charge_day": 10},
        {"id": 3, "item_description": "Cloud AI Subscription", "amount": 20, "currency": "USD", "category": "Learning", "payment_method": "Digital Wallet", "charge_day": 9},
        {"id": 4, "item_description": "Gym Membership", "amount": 40, "currency": "EUR", "category": "Living", "payment_method": "Primary Credit Card", "charge_day": 1},
        {"id": 5, "item_description": "Rent", "amount": 650, "currency": "EUR", "category": "Living", "payment_method": "Primary Credit Card", "charge_day": 1},
    ])

print(f"daily_expenses: {len(rows)} rows")
print("Done.")
