"""
News Collector for Interview AI Companion.

Usage:
  python news_collector.py --collect          # Collect daily news for all categories
  python news_collector.py --post             # Create posts from last 3 days of news
  python news_collector.py --collect --post   # Both: collect then post

Requires ANTHROPIC_API_KEY environment variable or pass via --api-key.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import anthropic

# Add parent to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.data_manager import add_post, CATEGORIES, load_posts

NEWS_DIR = Path(__file__).resolve().parent / "news"
NEWS_DIR.mkdir(exist_ok=True)

# Map categories to search topics for richer news gathering
CATEGORY_TOPICS = {
    "PEGA": [
        "Pega Systems latest news updates",
        "PEGA CDH Customer Decision Hub new features",
        "Pega Platform releases case management BPM",
        "Pega GenAI Blueprint automation",
    ],
    "Salesforce": [
        "Salesforce latest news product updates",
        "Salesforce Einstein AI Agentforce features",
        "Salesforce Flow automation Lightning updates",
        "Salesforce Data Cloud integration news",
    ],
    "Appian": [
        "Appian low-code platform latest news",
        "Appian process automation AI updates",
        "Appian connected systems integration",
        "Appian records data fabric features",
    ],
    "AI/New Technology": [
        "Claude AI Anthropic latest features MCP",
        "GitHub Copilot AI coding assistant updates",
        "Cursor AI editor new features",
        "RAG retrieval augmented generation enterprise AI trends",
        "MCP Model Context Protocol AI agents",
    ],
    "GCP": [
        "Google Cloud Platform latest news updates",
        "GCP Vertex AI Gemini features",
        "Google Kubernetes Engine GKE updates",
        "BigQuery Cloud Run serverless Google Cloud",
    ],
    "XaaS": [
        "Everything as a Service XaaS cloud trends",
        "SaaS PaaS IaaS market growth enterprise adoption",
        "AIaaS AI as a Service platforms",
        "Cloud service models subscription economy trends",
    ],
    "AI Agents & MCP": [
        "AI agents autonomous systems latest developments",
        "Model Context Protocol MCP Anthropic updates",
        "AI agent frameworks LangChain CrewAI AutoGen",
        "Tool use function calling AI agents enterprise",
    ],
    "API Gateway & Integration": [
        "Apigee API management Google Cloud updates",
        "MuleSoft Anypoint platform integration news",
        "Kong API gateway Kubernetes updates",
        "API-first architecture microservices trends",
    ],
    "DevOps / Platform Engineering": [
        "Platform engineering internal developer platform trends",
        "GitOps ArgoCD Flux Kubernetes deployment",
        "Terraform Pulumi infrastructure as code updates",
        "DevOps CI/CD pipeline automation news",
    ],
    "Cybersecurity & Zero Trust": [
        "Zero Trust architecture enterprise security",
        "SASE secure access service edge updates",
        "AI-powered cybersecurity threat detection",
        "Cloud security compliance automation news",
    ],
    "GenAI & LLM Ops": [
        "Generative AI enterprise deployment trends",
        "LLMOps MLOps observability monitoring",
        "RAG retrieval augmented generation production",
        "Prompt engineering fine-tuning best practices",
    ],
    "ServiceNow": [
        "ServiceNow platform latest news updates",
        "ServiceNow Now Assist AI features",
        "ServiceNow ITSM HRSD CSM updates",
        "ServiceNow Flow Designer automation",
    ],
    "Data Engineering": [
        "Databricks Snowflake data platform updates",
        "dbt data transformation analytics engineering",
        "Apache Spark Kafka real-time streaming news",
        "Modern data stack trends data mesh lakehouse",
    ],
    "RPA": [
        "UiPath robotic process automation updates",
        "Automation Anywhere intelligent automation news",
        "Microsoft Power Automate RPA features",
        "Intelligent document processing IDP trends",
    ],
    "Edge AI & IoT": [
        "Edge AI on-device inference updates",
        "Industrial IoT smart manufacturing news",
        "Digital twins IoT enterprise applications",
        "NVIDIA Jetson edge computing AI trends",
    ],
}


def collect_news_for_category(client: anthropic.Anthropic, category: str) -> str:
    """Use Claude to generate a comprehensive news summary for a category."""
    topics = CATEGORY_TOPICS.get(category, [f"{category} latest news"])
    topics_str = "\n".join(f"- {t}" for t in topics)

    prompt = f"""You are a technical news researcher. Write a comprehensive daily news briefing for the technology category: **{category}**

Research areas to cover:
{topics_str}

Write a well-structured news briefing that includes:
1. **Top Headlines** (3-5 major news items with brief descriptions)
2. **Product Updates & Releases** (any new features, versions, or announcements)
3. **Industry Trends** (what's changing in this space)
4. **Interview-Relevant Insights** (key talking points someone preparing for an interview should know)

Date: {datetime.now().strftime('%B %d, %Y')}

Format as clean readable text with clear sections. Be specific with version numbers, feature names, and company announcements. Focus on the most recent and impactful developments."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def save_daily_news(category: str, content: str) -> Path:
    """Save news to a dated txt file."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Sanitize category name for filename
    safe_name = category.replace("/", "-").replace(" ", "_")
    filename = f"{safe_name}_{date_str}.txt"
    filepath = NEWS_DIR / filename

    header = f"{'=' * 60}\n"
    header += f"  {category} - Daily News Briefing\n"
    header += f"  Date: {datetime.now().strftime('%B %d, %Y')}\n"
    header += f"{'=' * 60}\n\n"

    filepath.write_text(header + content, encoding="utf-8")
    return filepath


def collect_daily_news(client: anthropic.Anthropic):
    """Collect news for all categories and save as txt files."""
    print(f"\n{'=' * 60}")
    print(f"  Daily News Collection - {datetime.now().strftime('%B %d, %Y')}")
    print(f"{'=' * 60}\n")

    for category in CATEGORIES:
        print(f"Collecting news for {category}...", end=" ", flush=True)
        try:
            content = collect_news_for_category(client, category)
            filepath = save_daily_news(category, content)
            print(f"Saved to {filepath.name}")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nAll news files saved to: {NEWS_DIR}")


def get_recent_news_files(category: str, days: int = 3) -> list[Path]:
    """Get news files for a category from the last N days."""
    safe_name = category.replace("/", "-").replace(" ", "_")
    files = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        filepath = NEWS_DIR / f"{safe_name}_{date_str}.txt"
        if filepath.exists():
            files.append(filepath)
    return files


def create_post_from_news(client: anthropic.Anthropic):
    """Read last 3 days of news files and create curated posts for each category."""
    print(f"\n{'=' * 60}")
    print(f"  Creating Posts from News - {datetime.now().strftime('%B %d, %Y')}")
    print(f"{'=' * 60}\n")

    for category in CATEGORIES:
        news_files = get_recent_news_files(category, days=3)
        if not news_files:
            print(f"No recent news files for {category}, skipping.")
            continue

        # Read all recent news
        combined_news = ""
        for f in news_files:
            combined_news += f"\n\n--- {f.stem} ---\n"
            combined_news += f.read_text(encoding="utf-8")

        # Truncate if too long
        if len(combined_news) > 8000:
            combined_news = combined_news[:8000] + "\n\n[Truncated]"

        print(f"Creating post for {category} from {len(news_files)} news file(s)...", end=" ", flush=True)

        try:
            prompt = f"""Based on the following news briefings collected over the past few days for {category}, create a single curated interview preparation post.

{combined_news}

Write a post that:
1. Summarizes the most important developments
2. Highlights what an interview candidate should know
3. Includes key talking points and technical details
4. Is structured with clear headers and bullet points
5. Ends with 3-5 potential interview questions based on this news

Title the post: "{category} Weekly Update - {datetime.now().strftime('%B %d, %Y')}"

Write in a professional but accessible tone."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}],
            )
            post_content = response.content[0].text

            # Check if a similar post already exists today
            today = datetime.now().strftime("%B %d, %Y")
            existing = load_posts()
            already_posted = any(
                p["category"] == category and today in p.get("title", "")
                for p in existing
            )

            if already_posted:
                print("Post already exists for today, skipping.")
                continue

            post = add_post(
                title=f"{category} Weekly Update - {today}",
                content=post_content,
                category=category,
                tags=["auto-generated", "news-update", "weekly"],
            )
            print(f"Post created: {post['title']}")

        except Exception as e:
            print(f"ERROR: {e}")

    print("\nDone! Posts added to the website.")


def main():
    parser = argparse.ArgumentParser(description="Interview AI Companion News Collector")
    parser.add_argument("--collect", action="store_true", help="Collect daily news for all categories")
    parser.add_argument("--post", action="store_true", help="Create posts from last 3 days of news")
    parser.add_argument("--api-key", type=str, help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    args = parser.parse_args()

    if not args.collect and not args.post:
        parser.print_help()
        sys.exit(1)

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide API key via --api-key or ANTHROPIC_API_KEY env var")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.collect:
        collect_daily_news(client)

    if args.post:
        create_post_from_news(client)


if __name__ == "__main__":
    main()
