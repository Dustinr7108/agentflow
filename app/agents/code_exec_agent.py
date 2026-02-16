"""Code Execution Agent - runs Python code in a sandboxed environment."""
import time
import sys
import io
import traceback
from app.agents.base import BaseAgent, AgentResult


class CodeExecAgent(BaseAgent):
    name = "code_exec"
    description = "Execute Python code safely and return results"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        code = self.config.get("code", objective)
        timeout = self.config.get("timeout", 30)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_out = io.StringIO()
        sys.stderr = captured_err = io.StringIO()

        safe_globals = {
            "__builtins__": {
                "print": print, "len": len, "range": range, "str": str,
                "int": int, "float": float, "list": list, "dict": dict,
                "tuple": tuple, "set": set, "bool": bool, "type": type,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "sorted": sorted, "reversed": reversed, "sum": sum, "min": min,
                "max": max, "abs": abs, "round": round, "isinstance": isinstance,
                "True": True, "False": False, "None": None,
            }
        }

        if context:
            safe_globals["context"] = context

        try:
            exec(code, safe_globals)
            stdout = captured_out.getvalue()
            stderr = captured_err.getvalue()

            result = safe_globals.get("result", stdout or "Code executed successfully")

            return AgentResult(
                success=True,
                output=result,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"stdout": stdout, "stderr": stderr},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Execution error: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
                metadata={"traceback": traceback.format_exc()},
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
