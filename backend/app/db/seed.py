import sqlite3
from typing import List, Tuple


def calculate_status(stock: int, reorder_level: int) -> str:
    """Calculates product stock health status dynamically."""
    if stock == 0:
        return "out_of_stock"
    elif stock <= reorder_level:
        return "low"
    return "healthy"


PRODUCTS_SEED = [
    ("P101", "Laptop Pro", "Computers", 2500.0, 4, 10),
    ("P102", "Wireless Headset", "Audio", 600.0, 31, 12),
    ("P103", "Mechanical Keyboard", "Peripherals", 700.0, 8, 10),
    ("P104", "Monitor 27", "Displays", 1800.0, 24, 8),
    ("P105", "USB-C Multi-Hub", "Accessories", 450.0, 0, 15),
    ("P106", "Ergonomic Mouse", "Peripherals", 350.0, 6, 10),
    ("P107", "Studio 4K Webcam", "Video", 850.0, 5, 10),
    ("P108", "Ultra-Wide Monitor 34", "Displays", 3200.0, 14, 5),
    ("P109", "Noise-Cancelling Earbuds", "Audio", 900.0, 22, 10),
    ("P110", "Smart Desk Lamp", "Office", 300.0, 40, 15),
    ("P111", "Portable SSD 1TB", "Storage", 1200.0, 18, 8),
    ("P112", "Aluminum Laptop Stand", "Accessories", 200.0, 35, 10),
    ("P113", "USB-C Fast Cable", "Accessories", 50.0, 80, 20),
]

SALES_SEED = [
    # April 2026: Total = 82,000
    ("TX-APR-01", "P101", 20, 2500.0, "2026-04-05"),
    ("TX-APR-02", "P104", 10, 1800.0, "2026-04-12"),
    ("TX-APR-03", "P102", 20, 600.0, "2026-04-19"),
    ("TX-APR-04", "P112", 10, 200.0, "2026-04-26"),

    # May 2026: Total = 91,000
    ("TX-MAY-01", "P101", 22, 2500.0, "2026-05-04"),
    ("TX-MAY-02", "P104", 12, 1800.0, "2026-05-11"),
    ("TX-MAY-03", "P103", 16, 700.0, "2026-05-18"),
    ("TX-MAY-04", "P102", 5, 600.0, "2026-05-22"),
    ("TX-MAY-05", "P113", 4, 50.0, "2026-05-28"),

    # June 2026: Total = 88,000
    ("TX-JUN-01", "P101", 20, 2500.0, "2026-06-06"),
    ("TX-JUN-02", "P108", 8, 3200.0, "2026-06-14"),
    ("TX-JUN-03", "P102", 15, 600.0, "2026-06-20"),
    ("TX-JUN-04", "P103", 4, 700.0, "2026-06-24"),
    ("TX-JUN-05", "P112", 3, 200.0, "2026-06-28"),

    # July 2026: Total = 101,000
    ("TX-JUL-01", "P101", 24, 2500.0, "2026-07-07"),
    ("TX-JUL-02", "P104", 15, 1800.0, "2026-07-15"),
    ("TX-JUL-03", "P103", 12, 700.0, "2026-07-21"),
    ("TX-JUL-04", "P102", 8, 600.0, "2026-07-25"),
    ("TX-JUL-05", "P112", 4, 200.0, "2026-07-29"),

    # August 2026: Total = 110,000
    ("TX-AUG-01", "P101", 26, 2500.0, "2026-08-05"),
    ("TX-AUG-02", "P108", 10, 3200.0, "2026-08-12"),
    ("TX-AUG-03", "P102", 15, 600.0, "2026-08-18"),
    ("TX-AUG-04", "P103", 5, 700.0, "2026-08-22"),
    ("TX-AUG-05", "P113", 10, 50.0, "2026-08-28"),

    # September 2026: Total = 124,500, Units = 248
    ("TX-SEP-01", "P101", 27, 2500.0, "2026-09-03"),  # 67,500
    ("TX-SEP-02", "P102", 42, 600.0, "2026-09-08"),   # 25,200
    ("TX-SEP-03", "P103", 31, 700.0, "2026-09-14"),   # 21,700
    ("TX-SEP-04", "P112", 18, 200.0, "2026-09-18"),   # 3,600
    ("TX-SEP-05", "P113", 130, 50.0, "2026-09-20"),  # 6,500
]

EMPLOYEES_BASE_SEED = [
    ("EMP-001", "Aarav Sharma", "Engineering", "Staff AI Engineer", "Active", 14),
    ("EMP-002", "Priya Patel", "Product", "Lead Product Manager", "Active", 12),
    ("EMP-003", "Rohan Verma", "Sales", "Account Executive", "On Leave", 8),
    ("EMP-004", "Ananya Iyer", "Operations", "Inventory Lead", "Active", 15),
    ("EMP-005", "Devansh Rao", "Engineering", "Systems Architect", "Active", 16),
    ("EMP-006", "Kavita Nair", "People & HR", "HR Generalist", "On Leave", 6),
    ("EMP-007", "Vikram Malhotra", "Finance", "Financial Analyst", "Active", 11),
    ("EMP-008", "Sneha Reddy", "Sales", "Sales Director", "Active", 18),
    ("EMP-009", "Arjun Kapoor", "Engineering", "Backend Engineer", "Active", 13),
    ("EMP-010", "Meera Joshi", "Product", "UI/UX Designer", "Active", 10),
    ("EMP-011", "Siddharth Joshi", "Operations", "Logistics Coordinator", "On Leave", 4),
    ("EMP-012", "Neha Gupta", "Engineering", "Frontend Specialist", "Active", 15),
    ("EMP-013", "Rajesh Pillai", "Sales", "Account Manager", "Active", 9),
    ("EMP-014", "Deepa Mehta", "People & HR", "Talent Partner", "Active", 14),
    ("EMP-015", "Kunal Singhania", "Engineering", "DevOps Engineer", "Active", 12),
    ("EMP-016", "Pooja Bose", "Product", "Product Analyst", "Active", 11),
]

# Expand the internal synthetic workforce to a larger mid-sized demo company (180 employees).
# The generation is deterministic so tests and demos remain reproducible.
_ADDITIONAL_FIRST_NAMES = [
    "Ishaan", "Aditi", "Kabir", "Riya", "Aditya", "Nisha", "Manav",
    "Simran", "Rahul", "Tanya", "Varun", "Isha", "Nikhil",
]
_ADDITIONAL_LAST_NAMES = [
    "Khanna", "Bansal", "Saxena", "Menon", "Chawla", "Desai", "Sethi", "Kulkarni", "Mishra", "Agarwal", "Bhatt", "Mukherjee", "Trivedi", "Dutta",
]
_DEPARTMENT_ROLES = [
    ("Engineering", "Software Engineer"),
    ("Product", "Product Manager"),
    ("Sales", "Account Executive"),
    ("Operations", "Supply Operations Analyst"),
    ("People & HR", "People Operations Specialist"),
    ("Finance", "Finance Analyst"),
    ("Customer Success", "Customer Success Manager"),
    ("Data & Analytics", "Data Analyst"),
    ("Marketing", "Marketing Specialist"),
    ("IT & Security", "Security Operations Analyst"),
    ("Legal & Compliance", "Compliance Analyst"),
    ("Procurement", "Procurement Specialist"),
]
_ADDITIONAL_ON_LEAVE_IDS = {26, 39, 52, 65, 78, 91, 104, 117, 130, 143, 156, 169, 176, 180}


def _build_additional_employees():
    employees = []
    for employee_id in range(17, 181):
        offset = employee_id - 17
        first = _ADDITIONAL_FIRST_NAMES[offset % len(_ADDITIONAL_FIRST_NAMES)]
        last = _ADDITIONAL_LAST_NAMES[offset // len(_ADDITIONAL_FIRST_NAMES)]
        department, role = _DEPARTMENT_ROLES[offset % len(_DEPARTMENT_ROLES)]
        status = "On Leave" if employee_id in _ADDITIONAL_ON_LEAVE_IDS else "Active"
        leave_balance = 6 + ((employee_id * 3) % 13)
        employees.append((
            f"EMP-{employee_id:03d}",
            f"{first} {last}",
            department,
            role,
            status,
            leave_balance,
        ))
    return employees


EMPLOYEES_SEED = EMPLOYEES_BASE_SEED + _build_additional_employees()


POLICIES_SEED = [
    (
        "policy_01",
        "Annual Leave",
        "18 days per year",
        "Full-time team members accrue 18 days of annual paid leave per calendar year. Up to 5 unused days may roll over into Q1 of the following year upon manager notification."
    ),
    (
        "policy_02",
        "Remote Work",
        "Up to 2 days per week",
        "Eligible team members may work remotely up to 2 days per business week. Core collaboration hours (10:00 - 16:00 IST) must be maintained for synchronous check-ins."
    ),
    (
        "policy_03",
        "Sick Leave",
        "10 days per year",
        "Team members are granted 10 paid sick days annually. A medical certificate is required for medical absences lasting 3 or more consecutive business days."
    ),
]

ACTIVITY_SEED = [
    ("act_001", "10:42", "sales", "Retrieved top products", "get_top_products", "success", 42),
    ("act_002", "10:43", "inventory", "Checked inventory", "get_product_stock", "success", 28),
    ("act_003", "10:44", "manager", "Generated final response", None, "success", 112),
]


def seed_database(conn: sqlite3.Connection) -> None:
    """
    Seeds initial database rows.
    Idempotent: Uses INSERT OR IGNORE so running multiple times will not duplicate rows.
    """
    cursor = conn.cursor()

    # Seed products
    for pid, name, cat, price, stock, reorder in PRODUCTS_SEED:
        status = calculate_status(stock, reorder)
        cursor.execute(
            """
            INSERT OR IGNORE INTO products (id, name, category, unit_price, stock, reorder_level, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (pid, name, cat, price, stock, reorder, status)
        )

    # Seed sales
    for tx_id, pid, qty, price, sdate in SALES_SEED:
        # Check if transaction already exists
        cursor.execute("SELECT id FROM sales WHERE transaction_id = ? AND product_id = ?", (tx_id, pid))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO sales (transaction_id, product_id, quantity, unit_price, sale_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tx_id, pid, qty, price, sdate)
            )

    # Seed employees
    for eid, name, dept, role, status, balance in EMPLOYEES_SEED:
        cursor.execute(
            """
            INSERT OR REPLACE INTO employees (id, name, department, role, status, leave_balance)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (eid, name, dept, role, status, balance)
        )

    # Seed HR policies
    for pol_id, title, summary, content in POLICIES_SEED:
        cursor.execute(
            """
            INSERT OR IGNORE INTO hr_policies (id, title, summary, content)
            VALUES (?, ?, ?, ?)
            """,
            (pol_id, title, summary, content)
        )

    # Seed activity logs
    for act_id, ts, agent, action, tool, status, dur in ACTIVITY_SEED:
        cursor.execute(
            """
            INSERT OR IGNORE INTO activity_logs (id, timestamp, agent, action, tool, status, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (act_id, ts, agent, action, tool, status, dur)
        )
