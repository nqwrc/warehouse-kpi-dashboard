-- Warehouse KPI database schema (SQLite)
-- Three tables mirroring the CSV files. Load them with: python build_db.py

CREATE TABLE IF NOT EXISTS products (
    sku          TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    storage_zone TEXT NOT NULL          -- '-18C' or '-25C'
);

CREATE TABLE IF NOT EXISTS lots (
    lot_code      TEXT PRIMARY KEY,
    sku           TEXT NOT NULL REFERENCES products (sku),
    received_date TEXT NOT NULL,        -- ISO date
    expiry_date   TEXT NOT NULL,        -- ISO date
    qty_received  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS order_lines (
    line_id     INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL,
    pick_date   TEXT NOT NULL,          -- ISO date
    picker_id   TEXT NOT NULL,
    sku         TEXT NOT NULL REFERENCES products (sku),
    lot_code    TEXT NOT NULL REFERENCES lots (lot_code),
    qty_ordered INTEGER NOT NULL,
    error_type  TEXT NOT NULL DEFAULT ''  -- '', wrong_qty, wrong_item, damaged, expired_lot
);

-- Indexes on the columns we filter and join on most often
CREATE INDEX IF NOT EXISTS idx_lines_date   ON order_lines (pick_date);
CREATE INDEX IF NOT EXISTS idx_lines_picker ON order_lines (picker_id);
CREATE INDEX IF NOT EXISTS idx_lines_sku    ON order_lines (sku);
