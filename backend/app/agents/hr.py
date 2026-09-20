"""
HR Specialist Agent for Phase B3.
Responsible for headcount, leave status, and corporate policy lookups.
Restricted exclusively to HR tools. No direct database or repository access.
"""

import time
import uuid
from typing import Optional
from .base import BaseAgent
from .types import AgentTask, AgentResult, ToolCallRecord
from ..tools.hr_tools import (
    get_employee_summary,
    get_employee_details,
    get_hr_policy,
    get_all_hr_policies_tool
)



class HRAgent(BaseAgent):
    name = "hr"
    description = "Specialist agent responsible for headcount, employee profiles, leave metrics, and corporate policies."

    ALLOWED_OPERATIONS = {
        "hr.summary",
        "hr.employee",
        "hr.policy",
        "hr.policies"
    }

    async def execute(self, task: AgentTask) -> AgentResult:
        if task.operation not in self.ALLOWED_OPERATIONS:
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                error={
                    "code": "UNSUPPORTED_OPERATION",
                    "message": f"Operation '{task.operation}' is not supported by HRAgent."
                }
            )

        db_path = task.parameters.get("db_path") or task.context.get("db_path")

        try:
            t0 = time.perf_counter()
            tool_name = ""
            result_data = {}
            summary = ""

            if task.operation == "hr.summary":
                tool_name = "get_employee_summary"
                result_data = get_employee_summary(db_path=db_path)
                summary = f"Employee summary: {result_data.get('employee_count')} employees across {result_data.get('departments')} depts, {result_data.get('employees_on_leave')} on leave"

            elif task.operation == "hr.employee":
                tool_name = "get_employee_details"
                emp_id = task.parameters.get("employee_id")
                result_data = get_employee_details(employee_id=emp_id, db_path=db_path)
                summary = f"Employee profile for {result_data.get('name')} ({result_data.get('role')})"

            elif task.operation == "hr.policy":
                tool_name = "get_hr_policy"
                title = task.parameters.get("title", "")
                result_data = get_hr_policy(title=title, db_path=db_path)
                summary = f"HR Policy: {result_data.get('title')} ({result_data.get('summary')})"

            elif task.operation == "hr.policies":
                tool_name = "get_all_hr_policies_tool"
                result_data = get_all_hr_policies_tool(db_path=db_path)
                summary = f"Retrieved {result_data.get('count')} corporate policies"

            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))

            call_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name,
                arguments=task.parameters,
                status="success",
                duration_ms=duration_ms,
                result_summary=summary
            )

            # Exactly one durable activity record per tool execution
            from ..services.business_service import BusinessService
            BusinessService.record_activity(
                agent=self.name,
                action=summary,
                tool=tool_name,
                status="success",
                duration_ms=duration_ms,
                db_path=db_path
            )

            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="success",
                data=result_data,
                tool_calls=[call_record]
            )

        except ValueError as ve:
            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))
            code = "POLICY_NOT_FOUND" if "policy" in (tool_name or "") else "EMPLOYEE_NOT_FOUND"
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "hr_tool",
                arguments=task.parameters,
                status="error",
                duration_ms=duration_ms,
                result_summary="Resource not found",
                error=str(ve)
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                data=None,
                tool_calls=[err_record],
                error={
                    "code": code,
                    "message": str(ve)
                }
            )

        except Exception as e:
            t1 = time.perf_counter()
            duration_ms = max(1, int((t1 - t0) * 1000))
            err_record = ToolCallRecord(
                id=f"tool_{uuid.uuid4().hex[:8]}",
                agent=self.name,
                tool=tool_name or "unknown",
                arguments=task.parameters,
                status="error",
                duration_ms=duration_ms,
                result_summary="Execution failed",
                error=str(e)
            )
            return AgentResult(
                task_id=task.task_id,
                agent=self.name,
                status="error",
                tool_calls=[err_record],
                error={
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": str(e)
                }
            )
