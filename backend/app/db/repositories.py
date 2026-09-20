import sqlite3
from typing import List, Dict, Any, Optional


def get_all_products(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    return [dict(row) for row in cursor.fetchall()]


def get_product_by_id(conn: sqlite3.Connection, product_id: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_product_by_name(conn: sqlite3.Connection, name: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE LOWER(name) = LOWER(?)", (name.strip(),))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_low_stock_products_db(conn: sqlite3.Connection, include_out_of_stock: bool = False) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    if include_out_of_stock:
        cursor.execute("SELECT * FROM products WHERE stock <= reorder_level ORDER BY stock ASC")
    else:
        cursor.execute("SELECT * FROM products WHERE stock > 0 AND stock <= reorder_level ORDER BY stock ASC")
    return [dict(row) for row in cursor.fetchall()]


def get_inventory_summary_db(conn: sqlite3.Connection) -> Dict[str, int]:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as out_of_stock FROM products WHERE stock = 0")
    out_of_stock = cursor.fetchone()["out_of_stock"]

    cursor.execute("SELECT COUNT(*) as low_stock FROM products WHERE stock > 0 AND stock <= reorder_level")
    low_stock = cursor.fetchone()["low_stock"]

    cursor.execute("SELECT COUNT(*) as healthy FROM products WHERE stock > reorder_level")
    healthy = cursor.fetchone()["healthy"]

    return {
        "total_products": total,
        "healthy": healthy,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    }


def get_all_sales(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.*, p.name as product_name
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
        """
    )
    return [dict(row) for row in cursor.fetchall()]


def get_sales_between_dates(conn: sqlite3.Connection, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.*, p.name as product_name
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.sale_date BETWEEN ? AND ?
        ORDER BY s.sale_date ASC
        """,
        (start_date, end_date)
    )
    return [dict(row) for row in cursor.fetchall()]


def get_monthly_sales_db(conn: sqlite3.Connection, month: int, year: int) -> Dict[str, Any]:
    cursor = conn.cursor()
    month_str = f"{year}-{month:02d}"
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(quantity * unit_price), 0.0) as revenue,
            COALESCE(SUM(quantity), 0) as units_sold,
            COUNT(*) as transactions
        FROM sales
        WHERE strftime('%Y-%m', sale_date) = ?
        """,
        (month_str,)
    )
    row = cursor.fetchone()
    return {
        "month": month,
        "year": year,
        "revenue": float(row["revenue"]),
        "units_sold": int(row["units_sold"]),
        "transactions": int(row["transactions"])
    }


def get_total_sales_all_time(conn: sqlite3.Connection) -> Dict[str, Any]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(quantity * unit_price), 0.0) as revenue,
            COALESCE(SUM(quantity), 0) as units_sold,
            COUNT(DISTINCT transaction_id) as orders
        FROM sales
        """
    )
    row = cursor.fetchone()
    return {
        "revenue": float(row["revenue"]),
        "units_sold": int(row["units_sold"]),
        "orders": int(row["orders"])
    }


def get_top_selling_products_db(
    conn: sqlite3.Connection,
    limit: int = 5,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    if month is not None and year is not None:
        month_str = f"{year}-{month:02d}"
        cursor.execute(
            """
            SELECT
                p.id,
                p.name,
                COALESCE(SUM(s.quantity), 0) as units_sold,
                COALESCE(SUM(s.quantity * s.unit_price), 0.0) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE strftime('%Y-%m', s.sale_date) = ?
            GROUP BY p.id, p.name
            ORDER BY revenue DESC, units_sold DESC
            LIMIT ?
            """,
            (month_str, limit)
        )
    else:
        cursor.execute(
            """
            SELECT
                p.id,
                p.name,
                COALESCE(SUM(s.quantity), 0) as units_sold,
                COALESCE(SUM(s.quantity * s.unit_price), 0.0) as revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY revenue DESC, units_sold DESC
            LIMIT ?
            """,
            (limit,)
        )
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "units_sold": int(row["units_sold"]),
            "revenue": float(row["revenue"])
        }
        for row in cursor.fetchall()
    ]


def get_sales_trend_db(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            strftime('%Y-%m', sale_date) as ym,
            COALESCE(SUM(quantity * unit_price), 0.0) as revenue,
            COALESCE(SUM(quantity), 0) as units_sold
        FROM sales
        GROUP BY ym
        ORDER BY ym ASC
        """
    )
    month_names = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    results = []
    for row in cursor.fetchall():
        ym = row["ym"]
        m_code = ym.split("-")[1]
        m_name = month_names.get(m_code, m_code)
        results.append({
            "period": ym,
            "month": m_name,
            "revenue": float(row["revenue"]),
            "units_sold": int(row["units_sold"])
        })
    return results


def get_all_employees(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY id ASC")
    return [dict(row) for row in cursor.fetchall()]


def get_employee_by_id(conn: sqlite3.Connection, employee_id: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_employee_summary_db(conn: sqlite3.Connection) -> Dict[str, int]:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM employees")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(DISTINCT department) as depts FROM employees")
    depts = cursor.fetchone()["depts"]

    cursor.execute("SELECT COUNT(*) as on_leave FROM employees WHERE LOWER(status) = 'on leave'")
    on_leave = cursor.fetchone()["on_leave"]

    return {
        "employee_count": total,
        "departments": depts,
        "employees_on_leave": on_leave
    }


def get_all_hr_policies(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hr_policies ORDER BY id ASC")
    return [dict(row) for row in cursor.fetchall()]


def get_hr_policy_by_title(conn: sqlite3.Connection, title: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hr_policies WHERE LOWER(title) LIKE LOWER(?)", (f"%{title.strip()}%",))
    row = cursor.fetchone()
    return dict(row) if row else None


def add_activity_log_db(
    conn: sqlite3.Connection,
    log_id: str,
    timestamp: str,
    agent: str,
    action: str,
    tool: Optional[str],
    status: str,
    duration_ms: Optional[int]
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activity_logs (id, timestamp, agent, action, tool, status, duration_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (log_id, timestamp, agent, action, tool, status, duration_ms)
    )


def get_activity_logs_db(conn: sqlite3.Connection, limit: int = 50) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY rowid DESC LIMIT ?", (limit,))
    return [dict(row) for row in cursor.fetchall()]
