"""LLM Agent - uses language models to process text tasks."""
import time
import json
from typing import Any
from app.agents.base import BaseAgent, AgentResult
from app.config import settings


class LLMAgent(BaseAgent):
    name = "llm"
    description = "General-purpose language model agent for text generation, analysis, and reasoning"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        model = self.config.get("model", settings.DEFAULT_MODEL)
        system_prompt = self.config.get("system_prompt", "You are a helpful AI assistant.")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 2000)

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append({
                "role": "user",
                "content": f"Context from previous steps:\n{json.dumps(context, indent=2, default=str)}"
            })

        messages.append({"role": "user", "content": objective})

        try:
            if settings.OPENAI_API_KEY:
                return self._call_openai(messages, model, temperature, max_tokens, start)
            elif settings.ANTHROPIC_API_KEY:
                return self._call_anthropic(messages, model, temperature, max_tokens, start)
            else:
                return self._call_ollama(messages, model, temperature, max_tokens, start)
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"LLM call failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
            )

    def _call_openai(self, messages, model, temperature, max_tokens, start) -> AgentResult:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0]
        tokens = resp.usage.total_tokens if resp.usage else 0
        cost = self._estimate_cost(model, resp.usage.prompt_tokens or 0, resp.usage.completion_tokens or 0) if resp.usage else 0
        return AgentResult(
            success=True,
            output=choice.message.content,
            tokens_used=tokens,
            cost_usd=cost,
            duration_ms=int((time.time() - start) * 1000),
            metadata={"model": model, "finish_reason": choice.finish_reason},
        )

    def _call_anthropic(self, messages, model, temperature, max_tokens, start) -> AgentResult:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_msg,
            messages=user_msgs,
        )
        tokens = resp.usage.input_tokens + resp.usage.output_tokens
        return AgentResult(
            success=True,
            output=resp.content[0].text,
            tokens_used=tokens,
            cost_usd=tokens * 0.000003,
            duration_ms=int((time.time() - start) * 1000),
            metadata={"model": "claude-sonnet-4-20250514"},
        )

    def _call_ollama(self, messages, model, temperature, max_tokens, start) -> AgentResult:
        import httpx
        resp = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120.0,
        )
        data = resp.json()
        return AgentResult(
            success=True,
            output=data.get("message", {}).get("content", ""),
            tokens_used=data.get("eval_count", 0),
            cost_usd=0.0,  # Local = free
            duration_ms=int((time.time() - start) * 1000),
            metadata={"model": model, "provider": "ollama"},
        )

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        rates = {
            "gpt-4o-mini": (0.00000015, 0.0000006),
            "gpt-4o": (0.0000025, 0.00001),
            "gpt-4-turbo": (0.00001, 0.00003),
        }
        input_rate, output_rate = rates.get(model, (0.000001, 0.000002))
        return (input_tokens * input_rate) + (output_tokens * output_rate)
