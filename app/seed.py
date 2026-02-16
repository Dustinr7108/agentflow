"""Seed builtin agent definitions so users have them out of the box."""
from app.db import SessionLocal
from app.models import AgentDef


BUILTIN_AGENTS = [
    {
        "name": "GPT Writer",
        "description": "General-purpose AI writer for articles, emails, reports, and creative content",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are a professional writer. Create clear, engaging content.",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        },
    },
    {
        "name": "Data Analyst",
        "description": "Analyze data and generate insights, charts descriptions, and recommendations",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are a data analyst. Analyze data thoroughly and provide actionable insights with supporting evidence.",
            "model": "gpt-4o-mini",
            "temperature": 0.3,
        },
    },
    {
        "name": "Code Assistant",
        "description": "Write, debug, and explain code in any programming language",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are an expert programmer. Write clean, well-documented code. Explain your approach.",
            "model": "gpt-4o-mini",
            "temperature": 0.2,
        },
    },
    {
        "name": "Web Researcher",
        "description": "Search the web for information on any topic",
        "agent_type": "web_search",
        "config": {"engine": "duckduckgo", "max_results": 5},
    },
    {
        "name": "Python Runner",
        "description": "Execute Python code for data processing, calculations, and automation",
        "agent_type": "code_exec",
        "config": {"timeout": 30},
    },
    {
        "name": "API Connector",
        "description": "Call any external REST API and process the response",
        "agent_type": "api_call",
        "config": {"method": "GET", "timeout": 30},
    },
    {
        "name": "Data Transformer",
        "description": "Filter, map, merge, and reshape data flowing between agents",
        "agent_type": "data_transform",
        "config": {"operation": "passthrough"},
    },
    {
        "name": "Condition Check",
        "description": "Route workflow based on if/else conditions",
        "agent_type": "conditional",
        "config": {"operator": "eq"},
    },
    {
        "name": "Sales Email Writer",
        "description": "Write compelling sales and outreach emails personalized to each prospect",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are an expert at writing cold emails that get responses. Keep emails short (under 150 words), personalized, and with a clear CTA.",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        },
    },
    {
        "name": "SEO Content Writer",
        "description": "Write SEO-optimized blog posts and articles",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are an SEO content specialist. Write articles optimized for search engines while remaining engaging and valuable. Include suggested meta descriptions and keywords.",
            "model": "gpt-4o-mini",
            "temperature": 0.6,
        },
    },
    {
        "name": "Social Media Manager",
        "description": "Create social media posts optimized for each platform",
        "agent_type": "llm",
        "config": {
            "system_prompt": "You are a social media strategist. Create platform-specific posts (Twitter: punchy + hashtags, LinkedIn: professional + value-driven, Instagram: visual descriptions + hashtags, Facebook: conversational + engaging).",
            "model": "gpt-4o-mini",
            "temperature": 0.8,
        },
    },
]


def seed_builtin_agents():
    """Create builtin agents if they don't exist yet."""
    db = SessionLocal()
    try:
        existing = db.query(AgentDef).filter(AgentDef.is_builtin == True).count()
        if existing > 0:
            return  # Already seeded

        for agent_data in BUILTIN_AGENTS:
            agent = AgentDef(
                name=agent_data["name"],
                description=agent_data["description"],
                agent_type=agent_data["agent_type"],
                config=agent_data["config"],
                is_builtin=True,
            )
            db.add(agent)

        db.commit()
        print(f"Seeded {len(BUILTIN_AGENTS)} builtin agents")
    finally:
        db.close()
