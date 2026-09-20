"""Business tools package for specialist agent execution."""
from .sales_tools import (
    get_total_sales,
    get_monthly_sales,
    get_top_products,
    get_sales_trend
)
from .inventory_tools import (
    get_product_stock,
    get_low_stock_products,
    get_inventory_summary,
    get_all_products_inventory
)
from .hr_tools import (
    get_employee_summary,
    get_employee_details,
    get_all_employees_tool,
    get_hr_policy,
    get_all_hr_policies_tool
)

__all__ = [
    "get_total_sales",
    "get_monthly_sales",
    "get_top_products",
    "get_sales_trend",
    "get_product_stock",
    "get_low_stock_products",
    "get_inventory_summary",
    "get_all_products_inventory",
    "get_employee_summary",
    "get_employee_details",
    "get_all_employees_tool",
    "get_hr_policy",
    "get_all_hr_policies_tool"
]
