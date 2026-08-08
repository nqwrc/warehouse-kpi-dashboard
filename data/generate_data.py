"""
Synthetic data generator for a refrigerated food warehouse.

Modeled on real operations: frozen-food SKUs stored in different temperature
zones, lot codes with expiry dates, and order lines picked by operators with
a small, realistic error rate (company target: < 1% error lines).

Run:  python data/generate_data.py
Outputs three CSV files in this folder: products.csv, lots.csv, order_lines.csv
"""

import random
import csv
from datetime import date, timedelta

random.seed(42)  # reproducible output

OUT_DIR = "data"
START = date(2026, 1, 5)   # first Monday of the simulated period
WEEKS = 26                 # six months of activity

# ---------------------------------------------------------------- products --
# (sku, product name, category, storage zone)
CATEGORIES = {
    "Vegetables":  ("-18C", ["Peas 450g", "Spinach cubes 600g", "Minestrone mix 1kg",
                             "Green beans 450g", "Grilled peppers 400g"]),
    "Fish":        ("-25C", ["Cod fillets 400g", "Breaded shrimp 300g", "Salmon portions 500g",
                             "Seafood mix 400g", "Sole fillets 350g"]),
    "Ice cream":   ("-25C", ["Vanilla tub 1L", "Chocolate sticks x6", "Lemon sorbet 750ml",
                             "Hazelnut cones x4", "Stracciatella tub 1L"]),
    "Ready meals": ("-18C", ["Lasagne 600g", "Pizza margherita x2", "Risotto mushrooms 350g",
                             "Cannelloni 500g", "Veg burger x4"]),
    "Meat":        ("-18C", ["Chicken cutlets 500g", "Meatballs 400g", "Turkey slices 300g"]),
    "Bakery":      ("-18C", ["Croissants x6", "Baguette x2", "Strudel 400g"]),
}

products = []
sku_counter = 1000
for category, (zone, names) in CATEGORIES.items():
    for name in names:
        products.append({
            "sku": f"SKU{sku_counter}",
            "product_name": name,
            "category": category,
            "storage_zone": zone,
        })
        sku_counter += 1

# -------------------------------------------------------------------- lots --
# Each SKU gets several lots received over time. Lot code format: L<year><week>-<seq>
lots = []
lot_seq = 1
for p in products:
    n_lots = random.randint(3, 6)
    for _ in range(n_lots):
        received = START + timedelta(days=random.randint(-60, WEEKS * 7 - 14))
        shelf_life = random.choice([120, 180, 270, 365])  # days, typical for frozen food
        lots.append({
            "lot_code": f"L{received.isocalendar()[0]}{received.isocalendar()[1]:02d}-{lot_seq:04d}",
            "sku": p["sku"],
            "received_date": received.isoformat(),
            "expiry_date": (received + timedelta(days=shelf_life)).isoformat(),
            "qty_received": random.choice([120, 240, 360, 480]),
        })
        lot_seq += 1

# ------------------------------------------------------------- order lines --
# Pickers work Mon-Sat. Volume is higher on Mon/Tue (weekend restock effect).
# Error types and their relative frequency reflect what actually goes wrong
# on the floor: wrong quantity is the most common mistake, expired-lot picks
# are rare because of systematic date checks.
PICKERS = [f"P{n:02d}" for n in range(1, 9)]
ERROR_TYPES = ["wrong_qty", "wrong_item", "damaged", "expired_lot"]
ERROR_WEIGHTS = [0.55, 0.25, 0.15, 0.05]

# per-picker skill: most are close to target, one struggles, one excels
picker_error_rate = {p: random.uniform(0.004, 0.011) for p in PICKERS}
picker_error_rate["P03"] = 0.019   # new hire, above the 1% target
picker_error_rate["P07"] = 0.002   # veteran

lots_by_sku = {}
for lot in lots:
    lots_by_sku.setdefault(lot["sku"], []).append(lot)

order_lines = []
line_id = 1
order_id = 5000
for week in range(WEEKS):
    for weekday in range(6):  # Monday to Saturday
        day = START + timedelta(weeks=week, days=weekday)
        daily_orders = random.randint(55, 75) if weekday < 2 else random.randint(35, 60)
        for _ in range(daily_orders):
            order_id += 1
            picker = random.choice(PICKERS)
            for _ in range(random.randint(2, 9)):  # lines per order
                product = random.choice(products)
                lot = random.choice(lots_by_sku[product["sku"]])
                qty = random.randint(1, 12)
                is_error = random.random() < picker_error_rate[picker]
                error_type = random.choices(ERROR_TYPES, ERROR_WEIGHTS)[0] if is_error else ""
                order_lines.append({
                    "line_id": line_id,
                    "order_id": order_id,
                    "pick_date": day.isoformat(),
                    "picker_id": picker,
                    "sku": product["sku"],
                    "lot_code": lot["lot_code"],
                    "qty_ordered": qty,
                    "error_type": error_type,
                })
                line_id += 1

# ------------------------------------------------------------------- write --
def write_csv(filename, rows):
    with open(f"{OUT_DIR}/{filename}", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"{filename}: {len(rows)} rows")

if __name__ == "__main__":
    write_csv("products.csv", products)
    write_csv("lots.csv", lots)
    write_csv("order_lines.csv", order_lines)
    print("Done. Data covers", WEEKS, "weeks starting", START.isoformat())
