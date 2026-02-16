"""Template router - pre-built workflow templates users can clone."""
from fastapi import APIRouter
from app.schemas import TemplateInfo, WorkflowGraph, WorkflowNode, WorkflowEdge

router = APIRouter(prefix="/templates", tags=["templates"])

# Pre-built workflow templates
TEMPLATES = [
    TemplateInfo(
        id="lead-research",
        name="Lead Research Pipeline",
        description="Search the web for leads, analyze them with AI, and generate outreach emails",
        category="marketing",
        agent_count=3,
        graph=WorkflowGraph(
            nodes=[
                WorkflowNode(id="search", agent_type="web_search", objective="Find potential leads for {industry}",
                             position={"x": 100, "y": 200}, config_overrides={"max_results": 10}),
                WorkflowNode(id="analyze", agent_type="llm", objective="Analyze these leads and rank by quality",
                             position={"x": 400, "y": 200},
                             config_overrides={"system_prompt": "You are a sales intelligence analyst. Analyze leads and rank by fit."}),
                WorkflowNode(id="email", agent_type="llm", objective="Write personalized outreach emails for the top 3 leads",
                             position={"x": 700, "y": 200},
                             config_overrides={"system_prompt": "You are an expert cold email copywriter. Write short, compelling outreach."}),
            ],
            edges=[
                WorkflowEdge(source_id="search", target_id="analyze"),
                WorkflowEdge(source_id="analyze", target_id="email"),
            ],
        ),
    ),
    TemplateInfo(
        id="content-pipeline",
        name="Content Creation Pipeline",
        description="Research a topic, generate an article, then create social media posts from it",
        category="content",
        agent_count=3,
        graph=WorkflowGraph(
            nodes=[
                WorkflowNode(id="research", agent_type="web_search", objective="Research the latest trends in {topic}",
                             position={"x": 100, "y": 200}, config_overrides={"max_results": 8}),
                WorkflowNode(id="article", agent_type="llm", objective="Write a comprehensive 800-word article based on the research",
                             position={"x": 400, "y": 200},
                             config_overrides={"system_prompt": "You are a professional content writer. Write engaging, SEO-optimized articles."}),
                WorkflowNode(id="social", agent_type="llm", objective="Create 5 social media posts (Twitter, LinkedIn, Facebook) from this article",
                             position={"x": 700, "y": 200},
                             config_overrides={"system_prompt": "You are a social media strategist. Create engaging posts optimized for each platform."}),
            ],
            edges=[
                WorkflowEdge(source_id="research", target_id="article"),
                WorkflowEdge(source_id="article", target_id="social"),
            ],
        ),
    ),
    TemplateInfo(
        id="competitor-analysis",
        name="Competitor Analysis",
        description="Search for competitors, analyze their strengths/weaknesses, and generate strategic recommendations",
        category="business",
        agent_count=3,
        graph=WorkflowGraph(
            nodes=[
                WorkflowNode(id="search", agent_type="web_search", objective="Find competitors for {business_type}",
                             position={"x": 100, "y": 200}),
                WorkflowNode(id="analyze", agent_type="llm", objective="Analyze competitor strengths and weaknesses from the search results",
                             position={"x": 400, "y": 200},
                             config_overrides={"system_prompt": "You are a business strategy consultant. Provide SWOT analysis."}),
                WorkflowNode(id="strategy", agent_type="llm", objective="Generate 5 actionable strategic recommendations based on the competitive analysis",
                             position={"x": 700, "y": 200},
                             config_overrides={"system_prompt": "You are a business strategist. Provide specific, actionable recommendations."}),
            ],
            edges=[
                WorkflowEdge(source_id="search", target_id="analyze"),
                WorkflowEdge(source_id="analyze", target_id="strategy"),
            ],
        ),
    ),
    TemplateInfo(
        id="data-enrichment",
        name="Data Enrichment Pipeline",
        description="Take raw data, call APIs to enrich it, then transform into a report",
        category="data",
        agent_count=3,
        graph=WorkflowGraph(
            nodes=[
                WorkflowNode(id="input", agent_type="data_transform", objective="Parse and validate input data",
                             position={"x": 100, "y": 200}, config_overrides={"operation": "passthrough"}),
                WorkflowNode(id="enrich", agent_type="api_call", objective="Enrich data with external API",
                             position={"x": 400, "y": 200}, config_overrides={"url": "", "method": "GET"}),
                WorkflowNode(id="report", agent_type="llm", objective="Generate a summary report from the enriched data",
                             position={"x": 700, "y": 200},
                             config_overrides={"system_prompt": "You are a data analyst. Create clear, actionable reports."}),
            ],
            edges=[
                WorkflowEdge(source_id="input", target_id="enrich"),
                WorkflowEdge(source_id="enrich", target_id="report"),
            ],
        ),
    ),
    TemplateInfo(
        id="conditional-alert",
        name="Smart Alert System",
        description="Monitor data, check conditions, and send alerts or take action based on results",
        category="automation",
        agent_count=4,
        graph=WorkflowGraph(
            nodes=[
                WorkflowNode(id="fetch", agent_type="api_call", objective="Fetch current data",
                             position={"x": 100, "y": 200}, config_overrides={"url": "", "method": "GET"}),
                WorkflowNode(id="check", agent_type="conditional", objective="Check if threshold exceeded",
                             position={"x": 350, "y": 200},
                             config_overrides={"field": "value", "operator": "gt", "value": "100"}),
                WorkflowNode(id="alert", agent_type="llm", objective="Generate alert message for the threshold breach",
                             position={"x": 600, "y": 100},
                             config_overrides={"system_prompt": "Generate a concise alert message."}),
                WorkflowNode(id="log", agent_type="data_transform", objective="Log normal reading",
                             position={"x": 600, "y": 300}, config_overrides={"operation": "passthrough"}),
            ],
            edges=[
                WorkflowEdge(source_id="fetch", target_id="check"),
                WorkflowEdge(source_id="check", target_id="alert", condition="true"),
                WorkflowEdge(source_id="check", target_id="log", condition="false"),
            ],
        ),
    ),
]


@router.get("/", response_model=list[TemplateInfo])
def list_templates():
    """List all available workflow templates."""
    return TEMPLATES


@router.get("/{template_id}", response_model=TemplateInfo)
def get_template(template_id: str):
    """Get a specific template."""
    for t in TEMPLATES:
        if t.id == template_id:
            return t
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Template not found")
