#!/usr/bin/env python3
"""
NEXUS -- Kaggle Dataset Importer (Phase D1B)
Safe, atomic ingestion of the Kaggle USA Toy Sales dataset into nexus_analytics.db.

- Fail-fast source file verification (existence, exact headers, SHA-256 hashes, row counts)
- Relational integrity verification (primary key uniqueness, foreign key validity, compound pair equivalence)
- Atomic database creation (writes to .tmp.db, runs full verification, promotes via os.replace)
- Enforces integer-cents financial storage (no floating-point rounding errors)
- Embeds dataset provenance and analytical assumptions in analytics_metadata table
- Creates specialized analytical indexes
- Preserves operational nexus.db completely untouched
"""

import os
import sys
import csv
import sqlite3
import hashlib
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Expected Source Files & Validation Constants
EXPECTED_FILES = {
    "stores": "stores.csv",
    "products": "products.csv",
    "inventory": "inventory.csv",
    "sales": "sales.csv"
}

EXPECTED_CHECKSUMS = {
    "stores.csv": "acc8b6201d40512bda9baa9a9e4140b4702780af6578ac88b6b8b5eb062afe4a",
    "products.csv": "9c5bec332c8ab670fb018e54c107cb7776b4c5241c9b7828b0f260b94d4573b4",
    "inventory.csv": "a3630b49956a43a811e19fba686b72e7c6071ca80e4274fcbc8c2c067721f201",
    "sales.csv": "882c0b579b8e9fab1a0fb1f37b04e3895ee7de76a07963fd588f352517adcc6f"
}

EXPECTED_HEADERS = {
    "stores.csv": ["Store_ID", "Store_Name", "Store_City", "Store_Location", "Store_Open_Date"],
    "products.csv": ["Product_ID", "Product_Name", "Product_Category", "Product_Cost", "Product_Price"],
    "inventory.csv": ["Store_ID", "Product_ID", "Stock_On_Hand"],
    "sales.csv": ["Sale_ID", "Date", "Store_ID", "Product_ID", "Units"]
}

EXPECTED_ROW_COUNTS = {
    "stores.csv": 120,
    "products.csv": 180,
    "inventory.csv": 14143,
    "sales.csv": 245800
}

EXPECTED_FINANCIAL_TOTALS = {
    "total_units": 567270,
    "revenue_cents": 986293325,    # $9,862,933.25
    "cogs_cents": 555682727,       # $5,556,827.27
    "profit_cents": 430610598,     # $4,306,105.98
    "total_stock": 338993,
    "zero_stock_placements": 321,
    "inventory_placements": 14143
}


class IngestionError(Exception):
    """Custom exception raised when source validation or ingestion fails."""
    pass


def compute_file_sha256(path: Path) -> str:
    """Calculates SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_money_to_cents(money_val: Any) -> int:
    """
    Parses currency string into exact integer minor units (cents).
    Rejects malformed strings or floating-point conversions.
    """
    if money_val is None:
        raise IngestionError("Null money value encountered.")
    money_str = str(money_val).strip()
    if not money_str:
        raise IngestionError("Empty money value encountered.")
    cleaned = money_str.replace("$", "").replace(",", "").strip()
    try:
        d = Decimal(cleaned)
    except InvalidOperation:
        raise IngestionError(f"Malformed monetary value: '{money_str}'")
    cents = int((d * 100).to_integral_value())
    if cents < 0:
        raise IngestionError(f"Negative monetary value not allowed: '{money_str}'")
    return cents


def validate_iso_date(date_val: Any) -> str:
    """
    Validates that date string is a genuine ISO-8601 calendar date (YYYY-MM-DD).
    Rejects invalid calendar dates.
    """
    if date_val is None:
        raise IngestionError("Null date value encountered.")
    date_str = str(date_val).strip()
    if not date_str:
        raise IngestionError("Empty date value encountered.")
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        if parsed.strftime("%Y-%m-%d") != date_str:
            raise IngestionError(f"Non-canonical date string: '{date_str}'")
        return date_str
    except ValueError as e:
        raise IngestionError(f"Invalid ISO calendar date '{date_str}': {e}")


def read_csv_clean_header(path: Path) -> Tuple[List[str], List[List[str]]]:
    """Reads CSV file, stripping any BOM markers from headers."""
    if not path.exists():
        raise IngestionError(f"Source file not found: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        try:
            raw_header = next(reader)
        except StopIteration:
            raise IngestionError(f"Source file is completely empty: {path}")
        cleaned_header = [col.strip().replace("\ufeff", "") for col in raw_header]
        rows = [row for row in reader]
    return cleaned_header, rows


def validate_source_files(
    source_dir: Path,
    check_checksums: bool = True,
    check_row_counts: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Fail-fast validation of raw CSV source files prior to touching destination database.
    """
    if verbose:
        print(" [1/5] Validating source files in:", source_dir)

    computed_hashes = {}
    parsed_tables = {}

    for name, filename in EXPECTED_FILES.items():
        file_path = source_dir / filename
        if not file_path.exists():
            raise IngestionError(f"Required dataset file missing: {file_path}")

        # Check SHA-256
        sha256_hash = compute_file_sha256(file_path)
        computed_hashes[filename] = sha256_hash
        if check_checksums:
            expected_hash = EXPECTED_CHECKSUMS.get(filename)
            if sha256_hash != expected_hash:
                raise IngestionError(
                    f"Checksum mismatch for {filename}:\n"
                    f"  Expected: {expected_hash}\n"
                    f"  Actual:   {sha256_hash}"
                )

        # Check exact header
        header, rows = read_csv_clean_header(file_path)
        expected_header = EXPECTED_HEADERS[filename]
        if header != expected_header:
            raise IngestionError(
                f"Column header mismatch in {filename}:\n"
                f"  Expected: {expected_header}\n"
                f"  Actual:   {header}"
            )

        # Check row count
        if check_row_counts:
            expected_count = EXPECTED_ROW_COUNTS[filename]
            if len(rows) != expected_count:
                raise IngestionError(
                    f"Row count mismatch in {filename}: expected {expected_count}, got {len(rows)}"
                )

        parsed_tables[filename] = (header, rows)
        if verbose:
            print(f"       [OK] {filename}: {len(rows):,} rows, hash verified.")

    # Cross-table referential integrity & primary key pre-validation
    stores_header, stores_rows = parsed_tables["stores.csv"]
    products_header, products_rows = parsed_tables["products.csv"]
    inv_header, inv_rows = parsed_tables["inventory.csv"]
    sales_header, sales_rows = parsed_tables["sales.csv"]

    # Stores
    store_ids = set()
    for r in stores_rows:
        try:
            sid = int(r[0].strip())
        except ValueError:
            raise IngestionError(f"Invalid integer Store_ID in stores.csv: {r[0]}")
        if sid in store_ids:
            raise IngestionError(f"Duplicate primary key Store_ID={sid} in stores.csv")
        store_ids.add(sid)
        validate_iso_date(r[4])

    # Products
    product_ids = set()
    for r in products_rows:
        try:
            pid = int(r[0].strip())
        except ValueError:
            raise IngestionError(f"Invalid integer Product_ID in products.csv: {r[0]}")
        if pid in product_ids:
            raise IngestionError(f"Duplicate primary key Product_ID={pid} in products.csv")
        product_ids.add(pid)
        cost_cents = parse_money_to_cents(r[3])
        price_cents = parse_money_to_cents(r[4])
        if price_cents < cost_cents:
            raise IngestionError(f"Product_ID={pid} price (${price_cents/100}) < cost (${cost_cents/100})")

    # Inventory
    inv_pairs = set()
    for r in inv_rows:
        try:
            sid = int(r[0].strip())
            pid = int(r[1].strip())
            stock = int(r[2].strip())
        except ValueError as e:
            raise IngestionError(f"Invalid numeric value in inventory.csv: {r} ({e})")
        if sid not in store_ids:
            raise IngestionError(f"Foreign key violation: inventory Store_ID={sid} not in stores.csv")
        if pid not in product_ids:
            raise IngestionError(f"Foreign key violation: inventory Product_ID={pid} not in products.csv")
        pair = (sid, pid)
        if pair in inv_pairs:
            raise IngestionError(f"Duplicate composite key (Store_ID={sid}, Product_ID={pid}) in inventory.csv")
        if stock < 0:
            raise IngestionError(f"Negative stock value in inventory.csv: {stock}")
        inv_pairs.add(pair)

    # Sales
    sale_ids = set()
    sales_pairs = set()
    for r in sales_rows:
        try:
            sale_id = int(r[0].strip())
            validate_iso_date(r[1])
            sid = int(r[2].strip())
            pid = int(r[3].strip())
            units = int(r[4].strip())
        except ValueError as e:
            raise IngestionError(f"Invalid numeric value in sales.csv: {r} ({e})")
        if sale_id in sale_ids:
            raise IngestionError(f"Duplicate primary key Sale_ID={sale_id} in sales.csv")
        if sid not in store_ids:
            raise IngestionError(f"Foreign key violation: sales Store_ID={sid} not in stores.csv")
        if pid not in product_ids:
            raise IngestionError(f"Foreign key violation: sales Product_ID={pid} not in products.csv")
        if units <= 0:
            raise IngestionError(f"Non-positive units in sales.csv: {units}")
        sale_ids.add(sale_id)
        sales_pairs.add((sid, pid))

    # Compound store-product pair check
    if check_row_counts:
        if sales_pairs != inv_pairs:
            missing_in_inv = len(sales_pairs - inv_pairs)
            missing_in_sales = len(inv_pairs - sales_pairs)
            raise IngestionError(
                f"Compound store-product pair mismatch: "
                f"{missing_in_inv} sales pairs missing in inventory, "
                f"{missing_in_sales} inventory pairs missing in sales."
            )

    return {
        "computed_hashes": computed_hashes,
        "parsed_tables": parsed_tables
    }


def create_schema(conn: sqlite3.Connection) -> None:
    """Executes DDL to create the approved D1A.1 schema in SQLite."""
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Metadata Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_metadata (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            dataset_name TEXT NOT NULL,
            dataset_source TEXT NOT NULL,
            dataset_nature TEXT NOT NULL,
            license TEXT NOT NULL,
            currency_code TEXT NOT NULL DEFAULT 'USD',
            sales_start_date TEXT NOT NULL,
            sales_end_date TEXT NOT NULL,
            inventory_snapshot_date TEXT NOT NULL,
            inventory_snapshot_date_is_assumed INTEGER NOT NULL CHECK (inventory_snapshot_date_is_assumed IN (0, 1)),
            stores_sha256 TEXT NOT NULL,
            products_sha256 TEXT NOT NULL,
            inventory_sha256 TEXT NOT NULL,
            sales_sha256 TEXT NOT NULL,
            loaded_at TEXT NOT NULL,
            notes TEXT
        );
    """)

    # 2. Stores Dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_stores (
            store_id INTEGER PRIMARY KEY,
            store_name TEXT NOT NULL,
            store_city TEXT NOT NULL,
            store_location TEXT NOT NULL,
            store_open_date TEXT NOT NULL
        );
    """)

    # 3. Products Dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_category TEXT NOT NULL,
            product_cost_cents INTEGER NOT NULL CHECK (product_cost_cents >= 0),
            product_price_cents INTEGER NOT NULL CHECK (product_price_cents >= product_cost_cents)
        );
    """)

    # 4. Inventory Snapshot Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_inventory (
            store_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            stock_on_hand INTEGER NOT NULL CHECK (stock_on_hand >= 0),
            PRIMARY KEY (store_id, product_id),
            FOREIGN KEY (store_id) REFERENCES external_stores(store_id) ON DELETE RESTRICT,
            FOREIGN KEY (product_id) REFERENCES external_products(product_id) ON DELETE RESTRICT
        );
    """)

    # 5. Sales Fact Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_sales (
            sale_id INTEGER PRIMARY KEY,
            sale_date TEXT NOT NULL,
            store_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            units INTEGER NOT NULL CHECK (units > 0),
            FOREIGN KEY (store_id) REFERENCES external_stores(store_id) ON DELETE RESTRICT,
            FOREIGN KEY (product_id) REFERENCES external_products(product_id) ON DELETE RESTRICT
        );
    """)


def create_indexes(conn: sqlite3.Connection) -> None:
    """Creates specialized analytical indexes after bulk data loading."""
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_sales_date ON external_sales(sale_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_sales_product ON external_sales(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_sales_store ON external_sales(store_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_sales_covering ON external_sales(product_id, sale_date, units);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_inv_product ON external_inventory(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_prod_category ON external_products(product_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ext_store_location ON external_stores(store_location);")


def populate_database(
    conn: sqlite3.Connection,
    parsed_tables: Dict[str, Any],
    hashes: Dict[str, str],
    batch_size: int = 25000
) -> None:
    """Loads normalized parsed rows into SQLite using parameterized queries."""
    cursor = conn.cursor()

    # 1. Insert Metadata
    loaded_at_iso = datetime.now(timezone.utc).isoformat()
    notes_text = (
        "USA Toy Sales synthetic retail dataset (Kaggle / CC0). "
        "Inventory snapshot date (2025-12-31) is an analytical assumption; the source inventory.csv contains no timestamp. "
        "Historical sales contain 2,607 transactions across 3 stores (Stores 38, 59, 107) occurring prior to recorded opening dates, "
        "identified as a synthetic data generator artifact. Dataset is synthetic and not actual company operational data."
    )

    cursor.execute("""
        INSERT INTO analytics_metadata (
            id, dataset_name, dataset_source, dataset_nature, license, currency_code,
            sales_start_date, sales_end_date, inventory_snapshot_date, inventory_snapshot_date_is_assumed,
            stores_sha256, products_sha256, inventory_sha256, sales_sha256, loaded_at, notes
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "USA Toy Sales Dataset",
        "Kaggle",
        "Synthetic retail business dataset",
        "CC0 / Public Domain",
        "USD",
        "2025-01-01",
        "2025-12-31",
        "2025-12-31",
        1,
        hashes.get("stores.csv", ""),
        hashes.get("products.csv", ""),
        hashes.get("inventory.csv", ""),
        hashes.get("sales.csv", ""),
        loaded_at_iso,
        notes_text
    ))

    # 2. Insert Stores
    _, stores_rows = parsed_tables["stores.csv"]
    stores_data = [
        (int(r[0].strip()), r[1].strip(), r[2].strip(), r[3].strip(), validate_iso_date(r[4]))
        for r in stores_rows
    ]
    cursor.executemany("""
        INSERT INTO external_stores (store_id, store_name, store_city, store_location, store_open_date)
        VALUES (?, ?, ?, ?, ?)
    """, stores_data)

    # 3. Insert Products
    _, products_rows = parsed_tables["products.csv"]
    products_data = [
        (int(r[0].strip()), r[1].strip(), r[2].strip(), parse_money_to_cents(r[3]), parse_money_to_cents(r[4]))
        for r in products_rows
    ]
    cursor.executemany("""
        INSERT INTO external_products (product_id, product_name, product_category, product_cost_cents, product_price_cents)
        VALUES (?, ?, ?, ?, ?)
    """, products_data)

    # 4. Insert Inventory
    _, inv_rows = parsed_tables["inventory.csv"]
    inv_data = [
        (int(r[0].strip()), int(r[1].strip()), int(r[2].strip()))
        for r in inv_rows
    ]
    cursor.executemany("""
        INSERT INTO external_inventory (store_id, product_id, stock_on_hand)
        VALUES (?, ?, ?)
    """, inv_data)

    # 5. Insert Sales in Batches
    _, sales_rows = parsed_tables["sales.csv"]
    sales_data_buffer = []
    for r in sales_rows:
        sales_data_buffer.append((
            int(r[0].strip()),
            validate_iso_date(r[1]),
            int(r[2].strip()),
            int(r[3].strip()),
            int(r[4].strip())
        ))
        if len(sales_data_buffer) >= batch_size:
            cursor.executemany("""
                INSERT INTO external_sales (sale_id, sale_date, store_id, product_id, units)
                VALUES (?, ?, ?, ?, ?)
            """, sales_data_buffer)
            sales_data_buffer.clear()

    if sales_data_buffer:
        cursor.executemany("""
            INSERT INTO external_sales (sale_id, sale_date, store_id, product_id, units)
            VALUES (?, ?, ?, ?, ?)
        """, sales_data_buffer)
        sales_data_buffer.clear()


def verify_database_integrity(
    conn: sqlite3.Connection,
    check_expected_totals: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Executes deep post-ingestion verification queries:
    - SQLite integrity_check & foreign_key_check
    - Exact table counts
    - Compound key equivalence
    - Integer cent financial aggregation audit
    - Inventory unit balances
    """
    cursor = conn.cursor()

    # 1. SQLite Pragma Checks
    cursor.execute("PRAGMA integrity_check;")
    integrity_result = cursor.fetchone()[0]
    if integrity_result != "ok":
        raise IngestionError(f"SQLite PRAGMA integrity_check failed: {integrity_result}")

    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    if fk_violations:
        raise IngestionError(f"SQLite PRAGMA foreign_key_check violations detected: {len(fk_violations)}")

    # 2. Table Row Counts
    cursor.execute("SELECT COUNT(*) FROM analytics_metadata;")
    meta_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM external_stores;")
    stores_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM external_products;")
    products_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM external_inventory;")
    inv_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM external_sales;")
    sales_count = cursor.fetchone()[0]

    if meta_count != 1:
        raise IngestionError(f"Expected 1 metadata row, found {meta_count}")

    if check_expected_totals:
        if stores_count != EXPECTED_ROW_COUNTS["stores.csv"]:
            raise IngestionError(f"Stores count mismatch: {stores_count}")
        if products_count != EXPECTED_ROW_COUNTS["products.csv"]:
            raise IngestionError(f"Products count mismatch: {products_count}")
        if inv_count != EXPECTED_ROW_COUNTS["inventory.csv"]:
            raise IngestionError(f"Inventory count mismatch: {inv_count}")
        if sales_count != EXPECTED_ROW_COUNTS["sales.csv"]:
            raise IngestionError(f"Sales count mismatch: {sales_count}")

    # 3. Compound Store/Product Pair Equivalence
    cursor.execute("SELECT COUNT(DISTINCT store_id || '-' || product_id) FROM external_sales;")
    distinct_sales_pairs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT store_id || '-' || product_id) FROM external_inventory;")
    distinct_inv_pairs = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM external_sales s
        WHERE NOT EXISTS (
            SELECT 1 FROM external_inventory i
            WHERE i.store_id = s.store_id AND i.product_id = s.product_id
        );
    """)
    sales_missing_inv = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM external_inventory i
        WHERE NOT EXISTS (
            SELECT 1 FROM external_sales s
            WHERE s.store_id = i.store_id AND s.product_id = i.product_id
        );
    """)
    inv_missing_sales = cursor.fetchone()[0]

    if check_expected_totals:
        if distinct_sales_pairs != 14143 or distinct_inv_pairs != 14143:
            raise IngestionError(f"Unexpected distinct pair counts: sales={distinct_sales_pairs}, inv={distinct_inv_pairs}")
        if sales_missing_inv != 0 or inv_missing_sales != 0:
            raise IngestionError(f"Compound pair incongruence: sales_missing_inv={sales_missing_inv}, inv_missing_sales={inv_missing_sales}")

    # 4. Financial Calculations in Integer Cents
    cursor.execute("SELECT SUM(units) FROM external_sales;")
    total_units = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT
            SUM(s.units * p.product_price_cents),
            SUM(s.units * p.product_cost_cents)
        FROM external_sales s
        JOIN external_products p ON s.product_id = p.product_id;
    """)
    rev_row = cursor.fetchone()
    revenue_cents = rev_row[0] or 0
    cogs_cents = rev_row[1] or 0
    gross_profit_cents = revenue_cents - cogs_cents

    if check_expected_totals:
        exp_units = EXPECTED_FINANCIAL_TOTALS["total_units"]
        exp_rev = EXPECTED_FINANCIAL_TOTALS["revenue_cents"]
        exp_cogs = EXPECTED_FINANCIAL_TOTALS["cogs_cents"]
        exp_profit = EXPECTED_FINANCIAL_TOTALS["profit_cents"]

        if total_units != exp_units:
            raise IngestionError(f"Financial unit sum mismatch: got {total_units}, expected {exp_units}")
        if revenue_cents != exp_rev:
            raise IngestionError(f"Revenue cents mismatch: got {revenue_cents}, expected {exp_rev}")
        if cogs_cents != exp_cogs:
            raise IngestionError(f"COGS cents mismatch: got {cogs_cents}, expected {exp_cogs}")
        if gross_profit_cents != exp_profit:
            raise IngestionError(f"Gross profit cents mismatch: got {gross_profit_cents}, expected {exp_profit}")

    # 5. Inventory Balances
    cursor.execute("SELECT SUM(stock_on_hand) FROM external_inventory;")
    total_stock = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM external_inventory WHERE stock_on_hand = 0;")
    zero_stock = cursor.fetchone()[0] or 0

    if check_expected_totals:
        if total_stock != EXPECTED_FINANCIAL_TOTALS["total_stock"]:
            raise IngestionError(f"Total stock mismatch: got {total_stock}")
        if zero_stock != EXPECTED_FINANCIAL_TOTALS["zero_stock_placements"]:
            raise IngestionError(f"Zero stock placement mismatch: got {zero_stock}")

    results = {
        "integrity": integrity_result,
        "fk_violations": len(fk_violations),
        "row_counts": {
            "metadata": meta_count,
            "stores": stores_count,
            "products": products_count,
            "inventory": inv_count,
            "sales": sales_count
        },
        "distinct_sales_pairs": distinct_sales_pairs,
        "distinct_inv_pairs": distinct_inv_pairs,
        "sales_missing_inv": sales_missing_inv,
        "inv_missing_sales": inv_missing_sales,
        "financials": {
            "total_units": total_units,
            "revenue_cents": revenue_cents,
            "cogs_cents": cogs_cents,
            "profit_cents": gross_profit_cents,
            "revenue_usd": revenue_cents / 100.0,
            "cogs_usd": cogs_cents / 100.0,
            "profit_usd": gross_profit_cents / 100.0,
            "margin_pct": (gross_profit_cents / revenue_cents * 100.0) if revenue_cents > 0 else 0.0
        },
        "inventory": {
            "total_stock": total_stock,
            "zero_stock_placements": zero_stock,
            "total_placements": inv_count
        }
    }

    if verbose:
        print(" [4/5] Verification checks passed completely.")
        print(f"       Integrity: {integrity_result} | FK Violations: 0")
        print(f"       Financials: ${results['financials']['revenue_usd']:,.2f} revenue, {total_units:,} units.")
        print(f"       Inventory:  {total_stock:,} units on hand across {inv_count:,} placements.")

    return results


def ingest_dataset(
    source_dir: Path,
    target_db_path: Path,
    check_checksums: bool = True,
    check_row_counts: bool = True,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Main ingestion coordinator. Performs:
    1. Fail-fast source validation.
    2. Construction into temporary SQLite DB (`.tmp.db`).
    3. Populates tables & creates indexes.
    4. Runs full relational, SQLite integrity, and financial checks.
    5. Atomic promotion to target_db_path via os.replace.
    """
    source_dir = Path(source_dir).resolve()
    target_db_path = Path(target_db_path).resolve()
    target_db_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Source Validation
    validation_res = validate_source_files(
        source_dir=source_dir,
        check_checksums=check_checksums,
        check_row_counts=check_row_counts,
        verbose=verbose
    )
    parsed_tables = validation_res["parsed_tables"]
    hashes = validation_res["computed_hashes"]

    # 2. Temporary Database Path
    tmp_db_path = target_db_path.with_suffix(".tmp.db")
    if tmp_db_path.exists():
        tmp_db_path.unlink()

    conn = None
    try:
        if verbose:
            print(f" [2/5] Creating schema in temporary staging database: {tmp_db_path.name}")
        conn = sqlite3.connect(str(tmp_db_path))
        conn.execute("PRAGMA foreign_keys = ON;")

        # 3. Create Schema & Populate
        create_schema(conn)
        if verbose:
            print(" [3/5] Ingesting CSV records & generating indexes...")
        populate_database(conn, parsed_tables, hashes)
        create_indexes(conn)
        conn.commit()

        # 4. Post-Import Verification against Temporary DB
        audit_results = verify_database_integrity(
            conn=conn,
            check_expected_totals=check_row_counts,
            verbose=verbose
        )

        # 5. Close connection before atomic promotion (mandatory on Windows)
        conn.close()
        conn = None

        if verbose:
            print(f" [5/5] Atomically promoting {tmp_db_path.name} -> {target_db_path.name}...")
        os.replace(tmp_db_path, target_db_path)
        if verbose:
            print(f" SUCCESS: Analytics database generated at {target_db_path}")

        audit_results["target_db_path"] = str(target_db_path)
        return audit_results

    except Exception as e:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        if tmp_db_path.exists():
            try:
                tmp_db_path.unlink()
            except Exception:
                pass
        raise IngestionError(f"Database build failed and was rolled back cleanly: {e}") from e


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS Kaggle Dataset Importer (Phase D1B)")
    parser.add_argument(
        "--source-dir",
        type=str,
        default="backend/data/external/usa_toy_sales/raw",
        help="Path to raw CSV dataset directory"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="backend/data/nexus_analytics.db",
        help="Path to target nexus_analytics.db file"
    )
    parser.add_argument(
        "--skip-checksums",
        action="store_true",
        help="Skip SHA-256 validation (for unit testing only)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress logging"
    )

    args = parser.parse_args()

    # Determine paths relative to repo root if run from backend/ or root
    source_dir = Path(args.source_dir)
    if not source_dir.is_absolute():
        if not source_dir.exists() and Path("data/external/usa_toy_sales/raw").exists():
            source_dir = Path("data/external/usa_toy_sales/raw")

    db_path = Path(args.db_path)
    if not db_path.is_absolute():
        if not db_path.parent.exists() and Path("data").exists():
            db_path = Path("data/nexus_analytics.db")

    print("==================================================")
    print("NEXUS -- D1B KAGGLE ANALYTICS INTAKE")
    print("==================================================")
    try:
        results = ingest_dataset(
            source_dir=source_dir,
            target_db_path=db_path,
            check_checksums=not args.skip_checksums,
            verbose=not args.quiet
        )
        print("\nSUMMARY REPORT:")
        print(f"  Target DB:       {results['target_db_path']}")
        print(f"  Stores Loaded:   {results['row_counts']['stores']:,}")
        print(f"  Products Loaded: {results['row_counts']['products']:,}")
        print(f"  Inventory Rows:  {results['row_counts']['inventory']:,}")
        print(f"  Sales Records:   {results['row_counts']['sales']:,}")
        print(f"  Gross Revenue:   ${results['financials']['revenue_usd']:,.2f} ({results['financials']['revenue_cents']:,} cents)")
        print(f"  COGS Basis:      ${results['financials']['cogs_usd']:,.2f} ({results['financials']['cogs_cents']:,} cents)")
        print(f"  Gross Profit:    ${results['financials']['profit_usd']:,.2f} ({results['financials']['profit_cents']:,} cents)")
        print(f"  Overall Margin:  {results['financials']['margin_pct']:.2f}%")
        print(f"  Total Inventory: {results['inventory']['total_stock']:,} units ({results['inventory']['zero_stock_placements']} zero-stock placements)")
        print(f"  Integrity:       {results['integrity'].upper()} (0 Foreign Key Violations)")
        print("==================================================")
    except IngestionError as err:
        print(f"\n[ERROR] Ingestion Aborted: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
