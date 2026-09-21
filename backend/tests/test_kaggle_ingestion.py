"""
Tests for Phase D1B: Kaggle Dataset Ingestion into nexus_analytics.db.
Validates fail-fast checks, schema constraints, financial cent arithmetic,
atomic staging/promotion, and relational integrity using temporary directories.
"""

import os
import csv
import sqlite3
import pytest
from pathlib import Path

from scripts.import_kaggle_dataset import (
    ingest_dataset,
    validate_source_files,
    parse_money_to_cents,
    validate_iso_date,
    IngestionError,
    EXPECTED_CHECKSUMS,
    EXPECTED_ROW_COUNTS,
    EXPECTED_FINANCIAL_TOTALS,
)


@pytest.fixture
def minimal_dataset(tmp_path):
    """Creates a valid minimal dataset for fast testing in a temporary directory."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)

    # stores.csv
    stores_path = raw_dir / "stores.csv"
    with open(stores_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Store_ID", "Store_Name", "Store_City", "Store_Location", "Store_Open_Date"])
        writer.writerow(["1", "Toy Haven Seattle", "Seattle, WA", "Downtown", "2020-01-15"])
        writer.writerow(["2", "Toy World Austin", "Austin, TX", "Commercial", "2021-06-20"])

    # products.csv
    products_path = raw_dir / "products.csv"
    with open(products_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product_ID", "Product_Name", "Product_Category", "Product_Cost", "Product_Price"])
        writer.writerow(["101", "Action Robot", "Action Figures", "$10.50", "$25.00"])
        writer.writerow(["102", "Puzzle Box", "Puzzles", "$4.00", "$9.99"])

    # inventory.csv (Store 1 has both products, Store 2 has both products)
    inv_path = raw_dir / "inventory.csv"
    with open(inv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Store_ID", "Product_ID", "Stock_On_Hand"])
        writer.writerow(["1", "101", "15"])
        writer.writerow(["1", "102", "0"])   # Stockout
        writer.writerow(["2", "101", "8"])
        writer.writerow(["2", "102", "20"])

    # sales.csv (all pairs match inventory)
    sales_path = raw_dir / "sales.csv"
    with open(sales_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Sale_ID", "Date", "Store_ID", "Product_ID", "Units"])
        writer.writerow(["1", "2025-01-10", "1", "101", "2"])
        writer.writerow(["2", "2025-01-11", "1", "102", "1"])
        writer.writerow(["3", "2025-01-12", "2", "101", "3"])
        writer.writerow(["4", "2025-01-13", "2", "102", "4"])

    return raw_dir


# --- 1. Unit Validation Tests ---

def test_parse_money_to_cents_valid():
    assert parse_money_to_cents("$12.54") == 1254
    assert parse_money_to_cents("12.54") == 1254
    assert parse_money_to_cents("$1,234.50") == 123450
    assert parse_money_to_cents("0") == 0
    assert parse_money_to_cents("$0.05") == 5


def test_parse_money_to_cents_invalid():
    with pytest.raises(IngestionError, match="Malformed monetary value"):
        parse_money_to_cents("abc")
    with pytest.raises(IngestionError, match="Empty money value"):
        parse_money_to_cents("")
    with pytest.raises(IngestionError, match="Null money value"):
        parse_money_to_cents(None)
    with pytest.raises(IngestionError, match="Negative monetary value"):
        parse_money_to_cents("-12.50")


def test_validate_iso_date_valid():
    assert validate_iso_date("2025-01-15") == "2025-01-15"
    assert validate_iso_date("1991-12-31") == "1991-12-31"


def test_validate_iso_date_invalid():
    with pytest.raises(IngestionError, match="Invalid ISO calendar date"):
        validate_iso_date("2025-02-30")  # Invalid day in Feb
    with pytest.raises(IngestionError, match="Invalid ISO calendar date"):
        validate_iso_date("not-a-date")
    with pytest.raises(IngestionError, match="Empty date value"):
        validate_iso_date("  ")


# --- 2. Fail-Fast Source Integrity Tests ---

def test_missing_csv_fails(tmp_path, minimal_dataset):
    # Delete sales.csv
    (minimal_dataset / "sales.csv").unlink()
    target_db = tmp_path / "test_out.db"

    with pytest.raises(IngestionError, match="Required dataset file missing"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()
    assert not (tmp_path / "test_out.tmp.db").exists()


def test_checksum_mismatch_fails(tmp_path, minimal_dataset):
    target_db = tmp_path / "test_out.db"
    # Calling with check_checksums=True against minimal mock data must fail SHA-256
    with pytest.raises(IngestionError, match="Checksum mismatch"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=True,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


def test_malformed_money_fails(tmp_path, minimal_dataset):
    products_path = minimal_dataset / "products.csv"
    with open(products_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product_ID", "Product_Name", "Product_Category", "Product_Cost", "Product_Price"])
        writer.writerow(["101", "Action Robot", "Action Figures", "INVALID_COST", "$25.00"])

    target_db = tmp_path / "test_out.db"
    with pytest.raises(IngestionError, match="Malformed monetary value"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


def test_price_less_than_cost_fails(tmp_path, minimal_dataset):
    products_path = minimal_dataset / "products.csv"
    with open(products_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product_ID", "Product_Name", "Product_Category", "Product_Cost", "Product_Price"])
        writer.writerow(["101", "Action Robot", "Action Figures", "$30.00", "$25.00"])  # cost > price

    target_db = tmp_path / "test_out.db"
    with pytest.raises(IngestionError, match="price .* < cost"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


def test_invalid_date_in_sales_fails(tmp_path, minimal_dataset):
    sales_path = minimal_dataset / "sales.csv"
    with open(sales_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Sale_ID", "Date", "Store_ID", "Product_ID", "Units"])
        writer.writerow(["1", "2025-13-45", "1", "101", "2"])

    target_db = tmp_path / "test_out.db"
    with pytest.raises(IngestionError, match="Invalid ISO calendar date"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


def test_duplicate_primary_key_fails(tmp_path, minimal_dataset):
    stores_path = minimal_dataset / "stores.csv"
    with open(stores_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Store_ID", "Store_Name", "Store_City", "Store_Location", "Store_Open_Date"])
        writer.writerow(["1", "Toy Haven Seattle", "Seattle, WA", "Downtown", "2020-01-15"])
        writer.writerow(["1", "Duplicate Store 1", "Portland, OR", "Mall", "2021-02-01"])

    target_db = tmp_path / "test_out.db"
    with pytest.raises(IngestionError, match="Duplicate primary key Store_ID=1"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


def test_foreign_key_violation_fails(tmp_path, minimal_dataset):
    sales_path = minimal_dataset / "sales.csv"
    with open(sales_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Sale_ID", "Date", "Store_ID", "Product_ID", "Units"])
        writer.writerow(["1", "2025-01-10", "999", "101", "2"])  # Store 999 does not exist

    target_db = tmp_path / "test_out.db"
    with pytest.raises(IngestionError, match="Foreign key violation: sales Store_ID=999"):
        ingest_dataset(
            source_dir=minimal_dataset,
            target_db_path=target_db,
            check_checksums=False,
            check_row_counts=False,
            verbose=False
        )
    assert not target_db.exists()


# --- 3. Full Successful Ingestion on Mock Data ---

def test_successful_mock_ingestion(tmp_path, minimal_dataset):
    target_db = tmp_path / "test_analytics.db"

    results = ingest_dataset(
        source_dir=minimal_dataset,
        target_db_path=target_db,
        check_checksums=False,
        check_row_counts=False,
        verbose=False
    )

    assert target_db.exists()
    assert not (tmp_path / "test_analytics.tmp.db").exists()

    conn = sqlite3.connect(str(target_db))
    cursor = conn.cursor()

    # Metadata checks
    cursor.execute("SELECT dataset_name, currency_code, inventory_snapshot_date_is_assumed FROM analytics_metadata WHERE id = 1;")
    meta = cursor.fetchone()
    assert meta[0] == "USA Toy Sales Dataset"
    assert meta[1] == "USD"
    assert meta[2] == 1

    # Table counts
    cursor.execute("SELECT COUNT(*) FROM external_stores;")
    assert cursor.fetchone()[0] == 2
    cursor.execute("SELECT COUNT(*) FROM external_products;")
    assert cursor.fetchone()[0] == 2
    cursor.execute("SELECT COUNT(*) FROM external_inventory;")
    assert cursor.fetchone()[0] == 4
    cursor.execute("SELECT COUNT(*) FROM external_sales;")
    assert cursor.fetchone()[0] == 4

    # Financial verification
    # Sale 1: Store 1, Prod 101 (cost 1050, price 2500), units 2 -> rev 5000, cogs 2100, profit 2900
    # Sale 2: Store 1, Prod 102 (cost 400, price 999), units 1 -> rev 999, cogs 400, profit 599
    # Sale 3: Store 2, Prod 101 (cost 1050, price 2500), units 3 -> rev 7500, cogs 3150, profit 4350
    # Sale 4: Store 2, Prod 102 (cost 400, price 999), units 4 -> rev 3996, cogs 1600, profit 2396
    # Total units: 10
    # Total rev: 5000 + 999 + 7500 + 3996 = 17495 cents ($174.95)
    # Total cogs: 2100 + 400 + 3150 + 1600 = 7250 cents ($72.50)
    # Total profit: 17495 - 7250 = 10245 cents ($102.45)
    cursor.execute("""
        SELECT
            SUM(s.units),
            SUM(s.units * p.product_price_cents),
            SUM(s.units * p.product_cost_cents)
        FROM external_sales s
        JOIN external_products p ON s.product_id = p.product_id;
    """)
    totals = cursor.fetchone()
    assert totals[0] == 10
    assert totals[1] == 17495
    assert totals[2] == 7250
    assert totals[1] - totals[2] == 10245

    # Stock verification
    cursor.execute("SELECT SUM(stock_on_hand) FROM external_inventory;")
    assert cursor.fetchone()[0] == 43  # 15 + 0 + 8 + 20
    cursor.execute("SELECT COUNT(*) FROM external_inventory WHERE stock_on_hand = 0;")
    assert cursor.fetchone()[0] == 1

    # SQLite integrity checks
    cursor.execute("PRAGMA integrity_check;")
    assert cursor.fetchone()[0] == "ok"
    cursor.execute("PRAGMA foreign_key_check;")
    assert len(cursor.fetchall()) == 0

    conn.close()


def test_importer_deterministic_behavior(tmp_path, minimal_dataset):
    db1 = tmp_path / "db1.db"
    db2 = tmp_path / "db2.db"

    res1 = ingest_dataset(minimal_dataset, db1, check_checksums=False, check_row_counts=False, verbose=False)
    res2 = ingest_dataset(minimal_dataset, db2, check_checksums=False, check_row_counts=False, verbose=False)

    assert res1["financials"] == res2["financials"]
    assert res1["inventory"] == res2["inventory"]
    assert res1["row_counts"] == res2["row_counts"]


# --- 4. Verification Against Real Dataset in Isolated Temp DB ---

def test_real_dataset_integrity_in_isolated_temp_db(tmp_path):
    """
    Runs the full ingestion against the authoritative raw Kaggle dataset into a temporary
    database. Strictly verifies that operational nexus.db is never touched and all 245,800
    rows, hashes, and financial calculations match the D1A.1 audit.
    """
    real_raw_dir = Path("data/external/usa_toy_sales/raw")
    if not real_raw_dir.exists():
        real_raw_dir = Path("backend/data/external/usa_toy_sales/raw")

    if not real_raw_dir.exists():
        pytest.skip("Authoritative raw dataset not found in local workspace.")

    isolated_db = tmp_path / "isolated_real_analytics.db"

    # Ingest into temp test db
    results = ingest_dataset(
        source_dir=real_raw_dir,
        target_db_path=isolated_db,
        check_checksums=True,
        check_row_counts=True,
        verbose=False
    )

    # 1. Exact Row Counts
    assert results["row_counts"]["metadata"] == 1
    assert results["row_counts"]["stores"] == EXPECTED_ROW_COUNTS["stores.csv"]
    assert results["row_counts"]["products"] == EXPECTED_ROW_COUNTS["products.csv"]
    assert results["row_counts"]["inventory"] == EXPECTED_ROW_COUNTS["inventory.csv"]
    assert results["row_counts"]["sales"] == EXPECTED_ROW_COUNTS["sales.csv"]

    # 2. Referential and Relational Integrity
    assert results["integrity"] == "ok"
    assert results["fk_violations"] == 0
    assert results["distinct_sales_pairs"] == 14143
    assert results["distinct_inv_pairs"] == 14143
    assert results["sales_missing_inv"] == 0
    assert results["inv_missing_sales"] == 0

    # 3. Exact Financial Cents Matches
    fin = results["financials"]
    assert fin["total_units"] == EXPECTED_FINANCIAL_TOTALS["total_units"]
    assert fin["revenue_cents"] == EXPECTED_FINANCIAL_TOTALS["revenue_cents"]
    assert fin["cogs_cents"] == EXPECTED_FINANCIAL_TOTALS["cogs_cents"]
    assert fin["profit_cents"] == EXPECTED_FINANCIAL_TOTALS["profit_cents"]
    assert fin["revenue_cents"] - fin["cogs_cents"] == fin["profit_cents"]

    # 4. Inventory Units
    inv = results["inventory"]
    assert inv["total_stock"] == EXPECTED_FINANCIAL_TOTALS["total_stock"]
    assert inv["zero_stock_placements"] == EXPECTED_FINANCIAL_TOTALS["zero_stock_placements"]
    assert inv["total_placements"] == EXPECTED_FINANCIAL_TOTALS["inventory_placements"]

    # 5. Guarantee production DBs were NOT touched
    operational_db = Path("data/nexus.db")
    if operational_db.exists():
        conn = sqlite3.connect(str(operational_db))
        cursor = conn.cursor()
        # Ensure external tables were NOT created in operational nexus.db
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'external_%';")
        assert len(cursor.fetchall()) == 0
        conn.close()
