"""Data Transform Agent - transforms, filters, and reshapes data between nodes."""
import time
import json
from app.agents.base import BaseAgent, AgentResult


class DataTransformAgent(BaseAgent):
    name = "data_transform"
    description = "Transform, filter, map, and reshape data flowing between agents"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        operation = self.config.get("operation", "passthrough")

        try:
            data = context or {}
            input_key = self.config.get("input_key")
            if input_key and input_key in data:
                data = data[input_key]

            if operation == "passthrough":
                result = data
            elif operation == "extract_field":
                field = self.config.get("field", "")
                result = self._extract(data, field)
            elif operation == "filter":
                condition_field = self.config.get("condition_field", "")
                condition_value = self.config.get("condition_value", "")
                result = self._filter(data, condition_field, condition_value)
            elif operation == "map":
                template = self.config.get("template", "{item}")
                result = self._map(data, template)
            elif operation == "aggregate":
                agg_type = self.config.get("agg_type", "count")
                result = self._aggregate(data, agg_type)
            elif operation == "merge":
                result = self._merge(data)
            elif operation == "json_parse":
                result = json.loads(data) if isinstance(data, str) else data
            else:
                result = data

            output_key = self.config.get("output_key")
            if output_key:
                result = {output_key: result}

            return AgentResult(
                success=True,
                output=result,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"operation": operation},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Transform failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
            )

    def _extract(self, data, field: str):
        parts = field.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                return None
        return current

    def _filter(self, data, field: str, value):
        if not isinstance(data, list):
            return data
        return [item for item in data if str(self._extract(item, field)) == str(value)]

    def _map(self, data, template: str):
        if not isinstance(data, list):
            return data
        return [template.replace("{item}", json.dumps(item, default=str)) for item in data]

    def _aggregate(self, data, agg_type: str):
        if not isinstance(data, list):
            return data
        if agg_type == "count":
            return {"count": len(data)}
        elif agg_type == "first":
            return data[0] if data else None
        elif agg_type == "last":
            return data[-1] if data else None
        return {"count": len(data)}

    def _merge(self, data):
        if isinstance(data, dict):
            merged = {}
            for v in data.values():
                if isinstance(v, dict):
                    merged.update(v)
            return merged
        return data
