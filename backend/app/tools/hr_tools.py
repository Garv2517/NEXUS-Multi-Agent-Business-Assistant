"""
Deterministic Human Resources business tools.
Queries workforce census, employee directories, and corporate policies from SQLite.
"""

from typing import Optional, Dict, Any, List
from ..db.connection import get_db
from ..db.repositories import (
    get_employee_summary_db,
    get_employee_by_id,
    get_all_employees,
    get_all_hr_policies,
    get_hr_policy_by_title
)


def get_employee_summary(db_path: Optional[str] = None) -> Dict[str, int]:
    """
    Computes total headcount, distinct department count, and team members currently on leave.
    """
    with get_db(db_path) as conn:
        summary = get_employee_summary_db(conn)
        return summary


def get_employee_details(employee_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves safe business profile for an employee by ID.
    Does not expose sensitive personal information.
    """
    if not employee_id or not employee_id.strip():
        raise ValueError("Employee ID must be supplied.")

    with get_db(db_path) as conn:
        emp = get_employee_by_id(conn, employee_id.strip())
        if not emp:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")

        return {
            "id": emp["id"],
            "name": emp["name"],
            "department": emp["department"],
            "role": emp["role"],
            "status": emp["status"],
            "leave_balance": emp["leave_balance"]
        }


def get_all_employees_tool(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns full directory of company employees with safe business fields.
    """
    with get_db(db_path) as conn:
        employees = get_all_employees(conn)
        return [
            {
                "id": e["id"],
                "name": e["name"],
                "department": e["department"],
                "role": e["role"],
                "status": e["status"],
                "leave_balance": e["leave_balance"]
            }
            for e in employees
        ]


def get_hr_policy(title: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Looks up a corporate policy by title.
    """
    if not title or not title.strip():
        raise ValueError("Policy title cannot be empty.")

    with get_db(db_path) as conn:
        policy = get_hr_policy_by_title(conn, title.strip())
        if not policy:
            raise ValueError(f"Policy '{title}' not found.")

        return {
            "id": policy["id"],
            "title": policy["title"],
            "summary": policy["summary"],
            "content": policy["content"]
        }


def get_all_hr_policies_tool(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns all company corporate policies.
    """
    with get_db(db_path) as conn:
        policies = get_all_hr_policies(conn)
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "summary": p["summary"],
                "content": p["content"]
            }
            for p in policies
        ]
