import streamlit as st
from utils.data_manager import (
    ensure_data_dir, load_posts, add_post, update_post, delete_post,
    get_posts_by_category, load_questions, get_questions_by_category,
    load_history, save_history_entry, CATEGORIES,
)
from utils.ai_engine import (
    get_client, generate_questions, evaluate_answer, chat_qa, generate_from_post,
)

st.set_page_config(
    page_title="AI Companion Journalist Agent",
    page_icon="🎯",
    layout="wide",
)

ensure_data_dir()

# --- Authentication ---
VALID_USERNAME = "Kirthivasan"
VALID_PASSWORD = "Pradtiksha"
PROTECTED_PAGES = ["Content Manager", "Practice Mode"]

# --- Session State Defaults ---
defaults = {
    "api_key": "",
    "chat_messages": [],
    "chat_category": "PEGA",
    "logged_in": False,
    "username": "",
    "practice": {
        "active": False,
        "questions": [],
        "current_index": 0,
        "answers": [],
        "scores": [],
        "completed": False,
    },
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Sidebar ---
st.sidebar.title("AI Companion Journalist Agent")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Content Manager", "Browse & Learn", "Practice Mode", "AI Chat"],
)

st.sidebar.markdown("---")

# --- Login / Logout ---
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    def do_login():
        if st.session_state.login_user == VALID_USERNAME and st.session_state.login_pass == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = st.session_state.login_user
        else:
            st.session_state.login_error = True

    st.sidebar.subheader("Login")
    st.sidebar.text_input("Username", key="login_user")
    st.sidebar.text_input("Password", type="password", key="login_pass")
    st.sidebar.button("Login", type="primary", on_click=do_login)
    if st.session_state.get("login_error"):
        st.sidebar.error("Invalid username or password")
        st.session_state.login_error = False

st.sidebar.markdown("---")
st.sidebar.subheader("Settings")
api_key = st.sidebar.text_input("Anthropic API Key", type="password", value=st.session_state.api_key)
if api_key:
    st.session_state.api_key = api_key

st.sidebar.markdown("---")
st.sidebar.caption("AI Companion Journalist Agent | Built with Streamlit + Claude AI")


# ============================================================
# PAGE: HOME
# ============================================================
if page == "Home":
    st.title("Welcome to AI Companion Journalist Agent")
    st.markdown("Your personal AI-powered interview preparation and tech news companion covering **15 hot IT topics**.")

    posts = load_posts()
    history = load_history()

    # Display categories in rows of 5
    for row_start in range(0, len(CATEGORIES), 5):
        row_cats = CATEGORIES[row_start:row_start + 5]
        cols = st.columns(5)
        for col, cat in zip(cols, row_cats):
            count = len([p for p in posts if p["category"] == cat])
            col.metric(cat, f"{count} posts")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Quick Stats")
        st.metric("Total Posts", len(posts))
        st.metric("Practice Sessions", len(history))
        if history:
            scores = [h.get("ai_score", 0) for h in history if "ai_score" in h]
            if scores:
                st.metric("Average Score", f"{sum(scores) / len(scores):.1f} / 10")

    with col_b:
        st.subheader("Recent Practice")
        if history:
            for entry in reversed(history[-5:]):
                score = entry.get("ai_score", "N/A")
                cat = entry.get("category", "")
                ts = entry.get("timestamp", "")[:10]
                q = entry.get("question", "")[:80]
                st.markdown(f"**{ts}** | {cat} | Score: {score}/10")
                st.caption(q)
        else:
            st.info("No practice sessions yet. Head to Practice Mode to get started!")


# ============================================================
# PAGE: CONTENT MANAGER
# ============================================================
elif page == "Content Manager":
    if not st.session_state.logged_in:
        st.title("Content Manager")
        st.warning("Please log in to access the Content Manager. Use the login form in the sidebar.")
        st.stop()
    st.title("Content Manager")
    st.markdown("Add, edit, and manage your interview preparation content.")

    tab_add, tab_view, tab_import = st.tabs(["Add Post", "View/Edit Posts", "Import"])

    with tab_add:
        with st.form("add_post_form"):
            title = st.text_input("Title")
            category = st.selectbox("Category", CATEGORIES)
            content = st.text_area("Content", height=300)
            tags_input = st.text_input("Tags (comma-separated)")
            submitted = st.form_submit_button("Add Post")
            if submitted and title and content:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                add_post(title, content, category, tags)
                st.success(f"Post '{title}' added successfully!")
                st.rerun()

    with tab_view:
        filter_cat = st.selectbox("Filter by Category", ["All"] + CATEGORIES, key="filter_cat")
        posts = load_posts()
        if filter_cat != "All":
            posts = [p for p in posts if p["category"] == filter_cat]

        if not posts:
            st.info("No posts found. Add some content to get started!")
        else:
            for post in posts:
                with st.expander(f"{post['category']} | {post['title']}"):
                    st.markdown(post["content"][:500] + ("..." if len(post["content"]) > 500 else ""))
                    if post.get("tags"):
                        st.caption(f"Tags: {', '.join(post['tags'])}")
                    st.caption(f"Created: {post['created_at'][:10]}")

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("Edit", key=f"edit_{post['id']}"):
                            st.session_state[f"editing_{post['id']}"] = True

                    with col_del:
                        if st.button("Delete", key=f"del_{post['id']}", type="secondary"):
                            delete_post(post["id"])
                            st.success("Post deleted.")
                            st.rerun()

                    if st.session_state.get(f"editing_{post['id']}"):
                        with st.form(f"edit_form_{post['id']}"):
                            new_title = st.text_input("Title", value=post["title"])
                            new_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(post["category"]))
                            new_content = st.text_area("Content", value=post["content"], height=200)
                            new_tags = st.text_input("Tags", value=", ".join(post.get("tags", [])))
                            if st.form_submit_button("Save Changes"):
                                tags = [t.strip() for t in new_tags.split(",") if t.strip()]
                                update_post(post["id"], title=new_title, category=new_cat, content=new_content, tags=tags)
                                st.session_state[f"editing_{post['id']}"] = False
                                st.success("Post updated!")
                                st.rerun()

    with tab_import:
        st.markdown("Import content from a text or markdown file.")
        uploaded = st.file_uploader("Upload .txt or .md file", type=["txt", "md"])
        import_cat = st.selectbox("Category for imported content", CATEGORIES, key="import_cat")
        if uploaded:
            file_content = uploaded.read().decode("utf-8")
            st.text_area("Preview", value=file_content[:1000], height=200, disabled=True)
            if st.button("Import as Post"):
                add_post(
                    title=uploaded.name.rsplit(".", 1)[0],
                    content=file_content,
                    category=import_cat,
                    tags=["imported"],
                )
                st.success(f"Imported '{uploaded.name}' as a new post!")
                st.rerun()


# ============================================================
# PAGE: BROWSE & LEARN
# ============================================================
elif page == "Browse & Learn":
    st.title("Browse & Learn")

    tabs = st.tabs(CATEGORIES)
    for tab, category in zip(tabs, CATEGORIES):
        with tab:
            cat_posts = get_posts_by_category(category)
            cat_questions = get_questions_by_category(category)

            if cat_posts:
                st.subheader("Your Posts")
                for post in cat_posts:
                    with st.expander(post["title"]):
                        st.markdown(post["content"])
                        if post.get("tags"):
                            st.caption(f"Tags: {', '.join(post['tags'])}")

                        if st.session_state.api_key:
                            if st.button("Generate Questions from This Post", key=f"gen_{post['id']}"):
                                with st.spinner("Generating questions..."):
                                    try:
                                        client = get_client(st.session_state.api_key)
                                        new_qs = generate_from_post(client, post["content"], post["title"], category)
                                        st.session_state[f"generated_{post['id']}"] = new_qs
                                    except Exception as e:
                                        st.error(f"Error: {e}")

                            if f"generated_{post['id']}" in st.session_state:
                                st.markdown("**Generated Questions:**")
                                for i, q in enumerate(st.session_state[f"generated_{post['id']}"], 1):
                                    st.markdown(f"{i}. {q['question']}")
                                    with st.expander("View Sample Answer"):
                                        st.markdown(q.get("sample_answer", ""))
                        else:
                            st.caption("Enter your API key in the sidebar to generate questions.")
            else:
                st.info(f"No posts for {category} yet. Add content in the Content Manager.")

            if cat_questions:
                st.subheader("Question Bank")
                for q in cat_questions:
                    difficulty_color = {"beginner": "green", "intermediate": "orange", "advanced": "red"}.get(q.get("difficulty", ""), "gray")
                    st.markdown(f"**Q:** {q['question']}")
                    st.caption(f"Difficulty: {q.get('difficulty', 'N/A')}")
                    with st.expander("Sample Answer"):
                        st.markdown(q.get("sample_answer", "No sample answer available."))


# ============================================================
# PAGE: PRACTICE MODE
# ============================================================
elif page == "Practice Mode":
    if not st.session_state.logged_in:
        st.title("Practice Mode")
        st.warning("Please log in to access Practice Mode. Use the login form in the sidebar.")
        st.stop()
    st.title("Practice Mode")

    if not st.session_state.api_key:
        st.warning("Please enter your Anthropic API key in the sidebar to use Practice Mode.")
    else:
        practice = st.session_state.practice

        if not practice["active"] and not practice["completed"]:
            st.subheader("Setup Your Practice Session")
            p_category = st.selectbox("Category", CATEGORIES, key="p_cat")
            p_difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"], key="p_diff")
            p_count = st.slider("Number of Questions", 1, 10, 5, key="p_count")

            if st.button("Start Practice", type="primary"):
                with st.spinner("Generating questions..."):
                    try:
                        client = get_client(st.session_state.api_key)
                        posts = get_posts_by_category(p_category)
                        questions = generate_questions(client, p_category, p_count, p_difficulty, posts)
                        st.session_state.practice = {
                            "active": True,
                            "category": p_category,
                            "questions": questions,
                            "current_index": 0,
                            "answers": [],
                            "scores": [],
                            "completed": False,
                        }
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")

        elif practice["active"] and not practice["completed"]:
            idx = practice["current_index"]
            total = len(practice["questions"])
            q = practice["questions"][idx]

            st.progress((idx) / total, text=f"Question {idx + 1} of {total}")
            st.subheader(f"Question {idx + 1}")
            st.markdown(f"**{q['question']}**")
            st.caption(f"Difficulty: {q.get('difficulty', 'N/A')} | Category: {q.get('category', '')}")

            answer = st.text_area("Your Answer", height=200, key=f"answer_{idx}")

            if st.button("Submit Answer", type="primary"):
                if answer.strip():
                    with st.spinner("Evaluating your answer..."):
                        try:
                            client = get_client(st.session_state.api_key)
                            posts = get_posts_by_category(practice.get("category", ""))
                            result = evaluate_answer(client, q["question"], answer, posts)
                            practice["answers"].append({"question": q["question"], "answer": answer, "result": result})
                            practice["scores"].append(result.get("score", 0))

                            save_history_entry({
                                "category": practice.get("category", ""),
                                "question": q["question"],
                                "user_answer": answer,
                                "ai_score": result.get("score", 0),
                                "ai_feedback": result.get("feedback", ""),
                            })

                            st.markdown(f"### Score: {result.get('score', 'N/A')} / 10")
                            st.markdown(f"**Feedback:** {result.get('feedback', '')}")

                            if result.get("strengths"):
                                st.markdown("**Strengths:**")
                                for s in result["strengths"]:
                                    st.markdown(f"- {s}")

                            if result.get("improvements"):
                                st.markdown("**Areas for Improvement:**")
                                for imp in result["improvements"]:
                                    st.markdown(f"- {imp}")

                            if result.get("model_answer"):
                                with st.expander("View Model Answer"):
                                    st.markdown(result["model_answer"])

                            if idx + 1 < total:
                                if st.button("Next Question"):
                                    practice["current_index"] += 1
                                    st.rerun()
                            else:
                                if st.button("View Summary"):
                                    practice["completed"] = True
                                    practice["active"] = False
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error evaluating answer: {e}")
                else:
                    st.warning("Please write an answer before submitting.")

        elif practice["completed"]:
            st.subheader("Practice Session Summary")
            scores = practice["scores"]
            avg = sum(scores) / len(scores) if scores else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Questions", len(scores))
            col2.metric("Average Score", f"{avg:.1f} / 10")
            col3.metric("Category", practice.get("category", ""))

            st.markdown("---")
            for i, entry in enumerate(practice["answers"], 1):
                with st.expander(f"Q{i}: {entry['question'][:80]}... | Score: {entry['result'].get('score', 'N/A')}/10"):
                    st.markdown(f"**Your Answer:** {entry['answer']}")
                    st.markdown(f"**Feedback:** {entry['result'].get('feedback', '')}")
                    if entry["result"].get("model_answer"):
                        st.markdown(f"**Model Answer:** {entry['result']['model_answer']}")

            if st.button("Start New Practice", type="primary"):
                st.session_state.practice = defaults["practice"].copy()
                st.rerun()

    # Practice History
    st.markdown("---")
    with st.expander("Practice History"):
        history = load_history()
        if history:
            for entry in reversed(history[-20:]):
                score = entry.get("ai_score", "N/A")
                cat = entry.get("category", "")
                ts = entry.get("timestamp", "")[:16].replace("T", " ")
                q = entry.get("question", "")[:100]
                st.markdown(f"**{ts}** | {cat} | Score: **{score}/10**")
                st.caption(q)
                st.markdown("---")
        else:
            st.info("No practice history yet.")


# ============================================================
# PAGE: AI CHAT
# ============================================================
elif page == "AI Chat":
    st.title("AI Journalist Chat")

    if not st.session_state.api_key:
        st.warning("Please enter your Anthropic API key in the sidebar to use AI Chat.")
    else:
        chat_cat = st.selectbox("Context Category", CATEGORIES, key="chat_cat_select")

        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me anything about interview preparation..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        client = get_client(st.session_state.api_key)
                        posts = get_posts_by_category(chat_cat)
                        response = chat_qa(client, st.session_state.chat_messages, posts)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
