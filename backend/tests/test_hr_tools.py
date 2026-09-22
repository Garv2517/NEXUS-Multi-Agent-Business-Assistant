import pytest
from app.tools.hr_tools import (
    get_employee_summary,
    get_employee_details,
    get_all_employees_tool,
    get_hr_policy,
    get_all_hr_policies_tool
)


def test_get_employee_summary(test_db):
    """Verifies employee summary counts from SQLite."""
    summary = get_employee_summary(db_path=test_db)
    assert summary["employee_count"] == 180
    assert summary["departments"] == 12
    assert summary["employees_on_leave"] == 17


def test_get_employee_details_valid(test_db):
    """Verifies retrieval of safe employee profile."""
    emp = get_employee_details("EMP-001", db_path=test_db)
    assert emp["id"] == "EMP-001"
    assert emp["name"] == "Aarav Sharma"
    assert emp["department"] == "Engineering"
    assert emp["role"] == "Staff AI Engineer"
    assert emp["status"] == "Active"


def test_get_employee_details_invalid_raises_error(test_db):
    """Verifies that unknown employee ID raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_employee_details("EMP-999", db_path=test_db)


def test_get_all_employees_tool(test_db):
    """Verifies employee directory list."""
    employees = get_all_employees_tool(db_path=test_db)
    assert len(employees) == 180
    assert all("name" in e and "role" in e for e in employees)


def test_get_hr_policy_valid(test_db):
    """Verifies HR policy lookup."""
    policy = get_hr_policy("Annual Leave", db_path=test_db)
    assert policy["title"] == "Annual Leave"
    assert "18 days" in policy["summary"]


def test_get_hr_policy_missing_raises_error(test_db):
    """Verifies that missing policy throws ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_hr_policy("Non-Existent Policy XYZ", db_path=test_db)


def test_get_all_hr_policies_tool(test_db):
    """Verifies list of all HR policies."""
    policies = get_all_hr_policies_tool(db_path=test_db)
    assert len(policies) == 3
    titles = [p["title"] for p in policies]
    assert "Annual Leave" in titles
    assert "Remote Work" in titles
    assert "Sick Leave" in titles
