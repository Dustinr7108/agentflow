"""Workflow Execution Engine - the core orchestrator.

Executes a workflow graph by:
1. Topologically sorting nodes based on edges
2. Running each node's agent with context from upstream nodes
3. Handling conditional branching
4. Tracking results, tokens, and costs per node
"""
import time
from datetime import datetime, timezone
from collections import defaultdict, deque
from app.agents.registry import get_agent
from app.agents.base import AgentResult


class WorkflowEngine:
    """Executes a workflow graph."""

    def __init__(self, graph: dict, agent_defs: dict[str, dict] | None = None):
        """
        Args:
            graph: {"nodes": [...], "edges": [...]}
            agent_defs: {agent_def_id: {agent_type, config, ...}} lookup
        """
        self.nodes = {n["id"]: n for n in graph.get("nodes", [])}
        self.edges = graph.get("edges", [])
        self.agent_defs = agent_defs or {}
        self.results: dict[str, dict] = {}
        self.total_tokens = 0
        self.total_cost = 0.0

    def run(self, input_data: dict | None = None) -> dict:
        """Execute the full workflow.

        Returns:
            {status, node_results, output_data, total_tokens, total_cost_usd, duration_ms}
        """
        start = time.time()
        execution_order = self._topological_sort()
        skipped_nodes: set[str] = set()

        # Initialize context with input data
        context_store: dict[str, dict] = {}
        if input_data:
            context_store["__input__"] = input_data

        for node_id in execution_order:
            if node_id in skipped_nodes:
                self.results[node_id] = {"status": "skipped", "output": None, "duration_ms": 0}
                continue

            node = self.nodes[node_id]
            node_start = time.time()

            # Build context from upstream nodes
            upstream_context = self._gather_context(node_id, context_store, input_data)

            # Get agent definition
            agent_def_id = node.get("agent_def_id", "")
            agent_def = self.agent_defs.get(agent_def_id, {})
            agent_type = node.get("agent_type") or agent_def.get("agent_type", "llm")

            # Merge configs: agent_def defaults + node overrides
            config = {**agent_def.get("config", {}), **node.get("config_overrides", {})}
            objective = node.get("objective", config.get("objective", ""))

            try:
                agent = get_agent(agent_type, config=config)
                result: AgentResult = agent.run(objective, context=upstream_context)

                self.results[node_id] = {
                    "status": "completed" if result.success else "failed",
                    "output": result.output,
                    "tokens_used": result.tokens_used,
                    "cost_usd": result.cost_usd,
                    "duration_ms": result.duration_ms,
                    "metadata": result.metadata,
                }

                self.total_tokens += result.tokens_used
                self.total_cost += result.cost_usd

                # Store output in context for downstream nodes
                context_store[node_id] = (
                    result.output if isinstance(result.output, dict)
                    else {"output": result.output}
                )

                # Handle conditional branching
                if agent_type == "conditional" and isinstance(result.output, dict):
                    branch = result.output.get("branch", "true")
                    skipped = self._get_skipped_branches(node_id, branch)
                    skipped_nodes.update(skipped)

                # Stop on failure if configured
                if not result.success and node.get("stop_on_failure", True):
                    self.results[node_id]["status"] = "failed"
                    return self._build_result("failed", start, node_id)

            except Exception as e:
                self.results[node_id] = {
                    "status": "error",
                    "output": str(e),
                    "duration_ms": int((time.time() - node_start) * 1000),
                }
                if node.get("stop_on_failure", True):
                    return self._build_result("failed", start, node_id)

        return self._build_result("completed", start)

    def _topological_sort(self) -> list[str]:
        """Sort nodes in execution order respecting edges."""
        in_degree: dict[str, int] = defaultdict(int)
        adjacency: dict[str, list[str]] = defaultdict(list)

        for node_id in self.nodes:
            in_degree.setdefault(node_id, 0)

        for edge in self.edges:
            src = edge["source_id"]
            tgt = edge["target_id"]
            adjacency[src].append(tgt)
            in_degree[tgt] += 1

        queue = deque([n for n in self.nodes if in_degree[n] == 0])
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order

    def _gather_context(self, node_id: str, context_store: dict, input_data: dict | None) -> dict:
        """Collect outputs from all upstream nodes as context."""
        upstream = {}

        # Include original input
        if input_data:
            upstream["input"] = input_data

        # Find all edges targeting this node
        for edge in self.edges:
            if edge["target_id"] == node_id:
                src = edge["source_id"]
                if src in context_store:
                    upstream[src] = context_store[src]

        return upstream

    def _get_skipped_branches(self, conditional_node_id: str, taken_branch: str) -> set[str]:
        """For conditional nodes, determine which downstream nodes to skip."""
        skipped = set()
        for edge in self.edges:
            if edge["source_id"] == conditional_node_id:
                edge_branch = edge.get("condition", "true")
                if edge_branch != taken_branch:
                    # Skip this branch and all its descendants
                    skipped.add(edge["target_id"])
                    skipped.update(self._get_all_descendants(edge["target_id"]))
        return skipped

    def _get_all_descendants(self, node_id: str) -> set[str]:
        """Get all nodes downstream of a given node."""
        descendants = set()
        queue = deque([node_id])
        while queue:
            current = queue.popleft()
            for edge in self.edges:
                if edge["source_id"] == current and edge["target_id"] not in descendants:
                    descendants.add(edge["target_id"])
                    queue.append(edge["target_id"])
        return descendants

    def _build_result(self, status: str, start: float, failed_node: str | None = None) -> dict:
        """Build the final execution result."""
        # Find the last completed node's output as the workflow output
        output = None
        for node_id in reversed(list(self.results.keys())):
            r = self.results[node_id]
            if r.get("status") == "completed":
                output = r.get("output")
                break

        return {
            "status": status,
            "node_results": self.results,
            "output_data": output,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "duration_ms": int((time.time() - start) * 1000),
            "failed_node": failed_node,
        }
