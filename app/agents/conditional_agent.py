"""Conditional Agent - routes workflow based on conditions."""
import time
import json
import operator
from app.agents.base import BaseAgent, AgentResult


OPERATORS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "contains": lambda a, b: b in str(a),
    "not_contains": lambda a, b: b not in str(a),
    "is_empty": lambda a, _: not a,
    "is_not_empty": lambda a, _: bool(a),
}


class ConditionalAgent(BaseAgent):
    name = "conditional"
    description = "Route workflow execution based on conditions - if/else branching"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        field = self.config.get("field", "")
        op = self.config.get("operator", "eq")
        value = self.config.get("value", "")

        data = context or {}
        actual = self._extract(data, field)
        op_fn = OPERATORS.get(op, operator.eq)

        try:
            # Type coerce for numeric comparisons
            if op in ("gt", "gte", "lt", "lte"):
                try:
                    actual = float(actual) if actual else 0
                    value = float(value) if value else 0
                except (ValueError, TypeError):
                    pass

            condition_met = op_fn(actual, value)

            return AgentResult(
                success=True,
                output={
                    "condition_met": condition_met,
                    "branch": "true" if condition_met else "false",
                    "evaluated": f"{field} {op} {value} => {condition_met}",
                },
                duration_ms=int((time.time() - start) * 1000),
                metadata={"field": field, "operator": op, "value": value, "actual": str(actual)},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Condition evaluation failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
            )

    def _extract(self, data, field: str):
        parts = field.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
