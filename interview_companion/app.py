import streamlit as st
from datetime import datetime
from utils.data_manager import (
    ensure_data_dir, load_posts, add_post, update_post, delete_post,
    get_posts_by_category, CATEGORIES,
)
from utils.ai_engine import get_client, chat_qa

st.set_page_config(
    page_title="AI Tech Journal",
    page_icon="📡",
    layout="wide",
)

ensure_data_dir()

# --- Authentication ---
VALID_USERNAME = "Kirthivasan"
VALID_PASSWORD = "Pradtiksha"

# --- Session State Defaults ---
defaults = {
    "api_key": "",
    "chat_messages": [],
    "chat_category": "PEGA",
    "logged_in": False,
    "username": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B, #FF8C00, #4B8BFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .article-card {
        border-left: 4px solid #FF4B4B;
        padding-left: 15px;
        margin-bottom: 10px;
    }
    .category-badge {
        background-color: #FF4B4B;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .date-badge {
        color: #888;
        font-size: 0.85rem;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("## 📡 AI Tech Journal")
st.sidebar.caption("Your one-stop destination for what's happening in tech")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Tech Digest", "Content Manager", "AI Chat"],
    captions=["Dashboard & Overview", "Browse all articles by topic", "Manage posts (Admin)", "Ask AI about any topic"],
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

    st.sidebar.subheader("Admin Login")
    st.sidebar.text_input("Username", key="login_user")
    st.sidebar.text_input("Password", type="password", key="login_pass")
    st.sidebar.button("Login", type="primary", on_click=do_login)
    if st.session_state.get("login_error"):
        st.sidebar.error("Invalid username or password")
        st.session_state.login_error = False

st.sidebar.markdown("---")
st.sidebar.subheader("AI Settings")
api_key = st.sidebar.text_input("Anthropic API Key", type="password", value=st.session_state.api_key)
if api_key:
    st.session_state.api_key = api_key

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Claude AI | Updated twice weekly")


# ============================================================
# PAGE: HOME
# ============================================================
if page == "Home":
    st.markdown('<p class="main-header">AI Tech Journal</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your one-stop destination to understand what\'s happening across 15 hot IT areas — updated twice weekly</p>', unsafe_allow_html=True)

    posts = load_posts()

    # Category overview in rows of 5
    for row_start in range(0, len(CATEGORIES), 5):
        row_cats = CATEGORIES[row_start:row_start + 5]
        cols = st.columns(5)
        for col, cat in zip(cols, row_cats):
            count = len([p for p in posts if p["category"] == cat])
            col.metric(cat, f"{count} articles")

    st.markdown("---")

    # Latest Articles
    st.subheader("Latest Articles")
    if posts:
        # Sort by date, newest first
        sorted_posts = sorted(posts, key=lambda p: p.get("created_at", ""), reverse=True)
        for post in sorted_posts[:10]:
            date_str = post.get("created_at", "")[:10]
            category = post.get("category", "")
            tags = post.get("tags", [])

            col_main, col_date = st.columns([5, 1])
            with col_main:
                with st.expander(f"📰  **{post['title']}**  —  {category}"):
                    st.markdown(post["content"])
                    if tags:
                        tag_str = " ".join([f"`{t}`" for t in tags])
                        st.caption(f"Tags: {tag_str}")
            with col_date:
                st.caption(f"📅 {date_str}")
    else:
        st.info("No articles yet. Content will appear here once the journal is populated.")

    # Sidebar-style summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Articles", len(posts))
    col2.metric("Categories Covered", len(CATEGORIES))
    col3.metric("Update Frequency", "2x / week")


# ============================================================
# PAGE: TECH DIGEST (replaces Browse & Learn)
# ============================================================
elif page == "Tech Digest":
    st.markdown('<p class="main-header">Tech Digest</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Deep dive into each technology area — browse the latest insights, trends, and updates</p>', unsafe_allow_html=True)

    tabs = st.tabs(CATEGORIES)
    for tab, category in zip(tabs, CATEGORIES):
        with tab:
            cat_posts = get_posts_by_category(category)

            if cat_posts:
                # Sort newest first
                cat_posts_sorted = sorted(cat_posts, key=lambda p: p.get("created_at", ""), reverse=True)

                st.markdown(f"### {category} — {len(cat_posts_sorted)} article(s)")
                st.markdown("---")

                for post in cat_posts_sorted:
                    date_str = post.get("created_at", "")[:10]
                    tags = post.get("tags", [])

                    st.markdown(f"#### 📰 {post['title']}")
                    st.caption(f"Published: {date_str}")
                    st.markdown(post["content"])

                    if tags:
                        tag_str = " ".join([f"`{t}`" for t in tags])
                        st.caption(f"Tags: {tag_str}")
                    st.markdown("---")
            else:
                st.info(f"No articles for **{category}** yet. New content is published twice weekly.")


# ============================================================
# PAGE: CONTENT MANAGER (Admin only)
# ============================================================
elif page == "Content Manager":
    if not st.session_state.logged_in:
        st.title("Content Manager")
        st.warning("This is an admin-only area. Please log in using the sidebar.")
        st.stop()

    st.markdown('<p class="main-header">Content Manager</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Add, edit, and manage journal articles (Admin only)</p>', unsafe_allow_html=True)

    tab_add, tab_view, tab_import = st.tabs(["Add Article", "View/Edit Articles", "Import"])

    with tab_add:
        with st.form("add_post_form"):
            title = st.text_input("Article Title")
            category = st.selectbox("Category", CATEGORIES)
            content = st.text_area("Article Content (Markdown supported)", height=300)
            tags_input = st.text_input("Tags (comma-separated)")
            submitted = st.form_submit_button("Publish Article", type="primary")
            if submitted and title and content:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                add_post(title, content, category, tags)
                st.success(f"Article '{title}' published successfully!")
                st.rerun()

    with tab_view:
        filter_cat = st.selectbox("Filter by Category", ["All"] + CATEGORIES, key="filter_cat")
        posts = load_posts()
        if filter_cat != "All":
            posts = [p for p in posts if p["category"] == filter_cat]

        if not posts:
            st.info("No articles found.")
        else:
            for post in sorted(posts, key=lambda p: p.get("created_at", ""), reverse=True):
                with st.expander(f"{post['category']} | {post['title']} ({post.get('created_at', '')[:10]})"):
                    st.markdown(post["content"][:500] + ("..." if len(post["content"]) > 500 else ""))
                    if post.get("tags"):
                        st.caption(f"Tags: {', '.join(post['tags'])}")

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("Edit", key=f"edit_{post['id']}"):
                            st.session_state[f"editing_{post['id']}"] = True
                    with col_del:
                        if st.button("Delete", key=f"del_{post['id']}", type="secondary"):
                            delete_post(post["id"])
                            st.success("Article deleted.")
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
                                st.success("Article updated!")
                                st.rerun()

    with tab_import:
        st.markdown("Import content from a text or markdown file.")
        uploaded = st.file_uploader("Upload .txt or .md file", type=["txt", "md"])
        import_cat = st.selectbox("Category for imported content", CATEGORIES, key="import_cat")
        if uploaded:
            file_content = uploaded.read().decode("utf-8")
            st.text_area("Preview", value=file_content[:1000], height=200, disabled=True)
            if st.button("Import as Article"):
                add_post(
                    title=uploaded.name.rsplit(".", 1)[0],
                    content=file_content,
                    category=import_cat,
                    tags=["imported"],
                )
                st.success(f"Imported '{uploaded.name}' as a new article!")
                st.rerun()


# ============================================================
# PAGE: AI CHAT
# ============================================================
elif page == "AI Chat":
    st.markdown('<p class="main-header">AI Tech Chat</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask AI anything about the tech topics covered in the journal</p>', unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.warning("Enter your Anthropic API key in the sidebar to start chatting.")
    else:
        chat_cat = st.selectbox("Topic Context", CATEGORIES, key="chat_cat_select")

        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about any tech topic..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Researching..."):
                    try:
                        client = get_client(st.session_state.api_key)
                        posts = get_posts_by_category(chat_cat)
                        response = chat_qa(client, st.session_state.chat_messages, posts)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
