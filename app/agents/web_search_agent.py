"""Web Search Agent - searches the web and extracts information."""
import time
import json
from app.agents.base import BaseAgent, AgentResult


class WebSearchAgent(BaseAgent):
    name = "web_search"
    description = "Search the web for information, scrape pages, and extract structured data"

    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        start = time.time()
        search_engine = self.config.get("engine", "duckduckgo")
        max_results = self.config.get("max_results", 5)

        try:
            if search_engine == "duckduckgo":
                results = self._search_ddg(objective, max_results)
            else:
                results = self._search_ddg(objective, max_results)

            return AgentResult(
                success=True,
                output=results,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"engine": search_engine, "result_count": len(results)},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Search failed: {str(e)}",
                duration_ms=int((time.time() - start) * 1000),
            )

    def _search_ddg(self, query: str, max_results: int) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return [
                    {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                    for r in results
                ]
        except ImportError:
            return [{"title": "DuckDuckGo search not available", "url": "", "snippet": "Install duckduckgo-search package"}]
