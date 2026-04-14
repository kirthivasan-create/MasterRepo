import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SEED_DIR = BASE_DIR / "seed_data"

POSTS_FILE = DATA_DIR / "posts.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"
HISTORY_FILE = DATA_DIR / "practice_history.json"

CATEGORIES = [
    "PEGA",
    "Salesforce",
    "Appian",
    "AI/New Technology",
    "GCP",
    "XaaS",
    "AI Agents & MCP",
    "API Gateway & Integration",
    "DevOps / Platform Engineering",
    "Cybersecurity & Zero Trust",
    "GenAI & LLM Ops",
    "ServiceNow",
    "Data Engineering",
    "RPA",
    "Edge AI & IoT",
]


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not QUESTIONS_FILE.exists():
        seed = SEED_DIR / "default_questions.json"
        if seed.exists():
            shutil.copy(seed, QUESTIONS_FILE)
        else:
            _write_json(QUESTIONS_FILE, [])
    # Always sync posts from seed data (merge new seed posts into existing)
    seed_posts = SEED_DIR / "default_posts.json"
    if seed_posts.exists():
        seed_data = _read_json(seed_posts)
        if POSTS_FILE.exists():
            existing = _read_json(POSTS_FILE)
            existing_titles = {p["title"] for p in existing}
            new_posts = [p for p in seed_data if p["title"] not in existing_titles]
            if new_posts:
                existing.extend(new_posts)
                _write_json(POSTS_FILE, existing)
        else:
            _write_json(POSTS_FILE, seed_data)
    elif not POSTS_FILE.exists():
        _write_json(POSTS_FILE, [])
    if not HISTORY_FILE.exists():
        _write_json(HISTORY_FILE, [])


def _read_json(path: Path) -> list:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Posts ---

def load_posts() -> list[dict]:
    return _read_json(POSTS_FILE)


def save_posts(posts: list[dict]):
    _write_json(POSTS_FILE, posts)


def add_post(title: str, content: str, category: str, tags: list[str]) -> dict:
    posts = load_posts()
    now = datetime.now().isoformat()
    post = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "category": category,
        "tags": tags,
        "created_at": now,
        "updated_at": now,
    }
    posts.append(post)
    save_posts(posts)
    return post


def update_post(post_id: str, **fields) -> dict | None:
    posts = load_posts()
    for post in posts:
        if post["id"] == post_id:
            for key, value in fields.items():
                if key in post:
                    post[key] = value
            post["updated_at"] = datetime.now().isoformat()
            save_posts(posts)
            return post
    return None


def delete_post(post_id: str) -> bool:
    posts = load_posts()
    filtered = [p for p in posts if p["id"] != post_id]
    if len(filtered) == len(posts):
        return False
    save_posts(filtered)
    return True


def get_posts_by_category(category: str) -> list[dict]:
    return [p for p in load_posts() if p["category"] == category]


# --- Questions ---

def load_questions() -> list[dict]:
    return _read_json(QUESTIONS_FILE)


def save_questions(questions: list[dict]):
    _write_json(QUESTIONS_FILE, questions)


def get_questions_by_category(category: str) -> list[dict]:
    return [q for q in load_questions() if q["category"] == category]


# --- Practice History ---

def load_history() -> list[dict]:
    return _read_json(HISTORY_FILE)


def save_history_entry(entry: dict):
    history = load_history()
    entry["id"] = str(uuid.uuid4())
    entry["timestamp"] = datetime.now().isoformat()
    history.append(entry)
    _write_json(HISTORY_FILE, history)
