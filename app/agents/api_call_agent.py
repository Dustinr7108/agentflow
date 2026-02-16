"""API Call Agent - makes HTTP requests to external APIs."""
import time
import json
from app.agents.base import BaseAgent, AgentResult


class APICallAgent(BaseAgent):
    name = "api_call"
    description = "Make HTTP requests to external APIs and return structured responses"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        url = self.config.get("url", "")
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body = self.config.get("body")
        timeout_sec = self.config.get("timeout", 30)

        # Allow template substitution from context
        if context:
            url = self._interpolate(url, context)
            if body and isinstance(body, str):
                body = self._interpolate(body, context)
            for k, v in headers.items():
                headers[k] = self._interpolate(v, context)

        try:
            import httpx
            with httpx.Client(timeout=timeout_sec) as client:
                if method == "GET":
                    resp = client.get(url, headers=headers)
                elif method == "POST":
                    resp = client.post(url, headers=headers, content=body)
                elif method == "PUT":
                    resp = client.put(url, headers=headers, content=body)
                elif method == "DELETE":
                    resp = client.delete(url, headers=headers)
                else:
                    return AgentResult(success=False, output=f"Unsupported method: {method}")

            try:
                output = resp.json()
            except (json.JSONDecodeError, ValueError):
                output = resp.text

            return AgentResult(
                success=resp.status_code < 400,
                output=output,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"status_code": resp.status_code, "url": url, "method": method},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"API call failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
            )

    def _interpolate(self, template: str, context: dict) -> str:
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template
