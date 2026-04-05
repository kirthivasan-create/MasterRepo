import json
import re
import anthropic


def get_client(api_key: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key)


def _parse_json_response(text: str):
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _build_posts_context(posts: list[dict]) -> str:
    if not posts:
        return "No user content available for this category."
    parts = []
    for p in posts[:10]:
        parts.append(f"### {p['title']}\n{p['content'][:2000]}")
    return "\n\n".join(parts)


def generate_questions(
    client: anthropic.Anthropic,
    category: str,
    num_questions: int,
    difficulty: str,
    user_posts: list[dict],
) -> list[dict]:
    context = _build_posts_context(user_posts)
    prompt = f"""Generate {num_questions} interview questions for the category: {category}
Difficulty level: {difficulty}

Use the following study material as context to make questions relevant:
{context}

Return a JSON array where each element has:
- "question": the interview question text
- "difficulty": "{difficulty}"
- "category": "{category}"
- "sample_answer": a brief model answer (2-3 sentences)

Return ONLY the JSON array, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_response(response.content[0].text)


def evaluate_answer(
    client: anthropic.Anthropic,
    question: str,
    user_answer: str,
    reference_posts: list[dict],
) -> dict:
    context = _build_posts_context(reference_posts)
    prompt = f"""You are a senior technical interviewer evaluating a candidate's answer.

Question: {question}

Candidate's Answer: {user_answer}

Reference material for context:
{context}

Evaluate the answer and return a JSON object with:
- "score": integer from 1 to 10
- "feedback": a paragraph of constructive feedback
- "strengths": array of 2-3 things the candidate did well
- "improvements": array of 2-3 areas for improvement
- "model_answer": a concise ideal answer (3-4 sentences)

Return ONLY the JSON object, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_response(response.content[0].text)


def chat_qa(
    client: anthropic.Anthropic,
    messages_history: list[dict],
    context_posts: list[dict],
) -> str:
    context = _build_posts_context(context_posts)
    system_prompt = f"""You are an encouraging and knowledgeable interview preparation companion.
Help the user prepare for technical interviews. Be conversational, provide examples,
and reference the user's own study material when relevant.

User's study material:
{context}

Give clear, practical answers. Use examples from real-world scenarios when helpful."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        messages=messages_history,
    )
    return response.content[0].text


def generate_from_post(
    client: anthropic.Anthropic,
    post_content: str,
    post_title: str,
    category: str,
    num_questions: int = 5,
) -> list[dict]:
    prompt = f"""Based on the following article/post, generate {num_questions} interview questions that test understanding of the concepts covered.

Title: {post_title}
Category: {category}
Content: {post_content[:3000]}

Return a JSON array where each element has:
- "question": the interview question
- "difficulty": one of "beginner", "intermediate", "advanced"
- "category": "{category}"
- "sample_answer": a brief model answer (2-3 sentences)

Return ONLY the JSON array, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_response(response.content[0].text)
