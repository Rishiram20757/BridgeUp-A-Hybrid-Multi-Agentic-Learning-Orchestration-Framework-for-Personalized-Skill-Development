import html
from datetime import datetime
from pathlib import Path

import streamlit as st

from bridgeup_langgraph.ui_runner import run_bridgeup
from agents.monitoring_agent import MonitoringAgent
from learning_tutor.tutor import LearningTutor


# ===========================================================
# PAGE CONFIG
# ===========================================================
st.set_page_config(
    page_title="BridgeUp AI",
    page_icon="🚀",
    layout="wide"
)


# ===========================================================
# THEME
# ===========================================================
st.markdown("""
<style>
:root {
    --bg: #f8fafc;
    --card: #ffffff;
    --primary: #2563eb;
    --primary-soft: #eff6ff;
    --success: #16a34a;
    --success-soft: #ecfdf5;
    --warning: #f97316;
    --text: #111827;
    --muted: #4b5563;
    --border: #e5e7eb;
    --shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 3.25rem;
    max-width: 1240px;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
.stMarkdown, .stCaption, p, li {
    color: var(--text);
}

[data-testid="stMetric"] {
    background: transparent;
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-weight: 800;
}

.top-nav {
    position: sticky;
    top: 3.25rem;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.25rem;
    background: rgba(255,255,255,0.96);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0.75rem 0.9rem;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    margin-bottom: 1.4rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 210px;
}

.brand-mark {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: var(--primary);
    color: #ffffff;
    font-weight: 900;
    font-size: 1.35rem;
    box-shadow: 0 12px 20px rgba(37, 99, 235, 0.24);
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: 0;
}

.brand-subtitle {
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: -0.2rem;
}

.nav-shell div[role="radiogroup"] {
    display: flex;
    justify-content: center;
    gap: 0.35rem;
    flex-wrap: wrap;
}

.nav-shell label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 999px;
    padding: 0.45rem 0.8rem;
    color: var(--muted);
    font-weight: 750;
    transition: all 0.15s ease;
}

.nav-shell label:hover {
    background: var(--primary-soft);
    border-color: #bfdbfe;
    color: var(--primary);
}

.nav-shell input:checked + div {
    color: var(--primary);
    font-weight: 850;
}

.nav-shell label:has(input:checked) {
    background: var(--primary-soft);
    border-color: #bfdbfe;
}

.stButton > button {
    background: var(--primary);
    color: #ffffff;
    border: 0;
    border-radius: 10px;
    padding: 0.55rem 0.95rem;
    font-weight: 800;
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
}

.stButton > button:hover {
    background: #1d4ed8;
    color: #ffffff;
    border: 0;
}

.hero {
    background:
        radial-gradient(circle at 18% 35%, rgba(22, 163, 74, 0.10), transparent 26%),
        radial-gradient(circle at 78% 18%, rgba(37, 99, 235, 0.10), transparent 30%),
        #ffffff;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3.25rem 2rem;
    text-align: center;
    box-shadow: var(--shadow);
    margin-bottom: 1.5rem;
}

.hero h1 {
    font-size: clamp(2.2rem, 6vw, 4.8rem);
    line-height: 1.04;
    color: var(--text);
    margin: 0 auto 1rem;
    max-width: 920px;
    letter-spacing: 0;
}

.hero .accent {
    color: var(--primary);
}

.hero p {
    max-width: 760px;
    margin: 0 auto;
    color: var(--muted);
    font-size: 1.18rem;
    line-height: 1.6;
}

.page-kicker {
    color: var(--primary);
    text-transform: uppercase;
    font-size: 0.78rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
}

.page-title {
    font-size: 2.15rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 0.35rem;
}

.page-copy {
    color: var(--muted);
    font-size: 1rem;
    max-width: 760px;
    margin-bottom: 1.25rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 1rem 0 1.6rem;
}

.stat-card, .panel, .learning-card, .job-card, .lesson-panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: var(--shadow);
}

.stat-card {
    padding: 1.35rem;
    min-height: 150px;
}

.stat-icon {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    font-weight: 900;
    margin-bottom: 1rem;
}

.stat-icon.blue { background: var(--primary-soft); color: var(--primary); }
.stat-icon.green { background: var(--success-soft); color: var(--success); }
.stat-icon.orange { background: #fff7ed; color: var(--warning); }

.stat-number {
    font-size: 2.15rem;
    line-height: 1;
    font-weight: 900;
    color: var(--text);
}

.stat-label {
    color: var(--muted);
    margin-top: 0.35rem;
}

.stat-note {
    color: var(--success);
    font-size: 0.9rem;
    font-weight: 800;
    margin-top: 0.75rem;
}

.panel {
    padding: 1.4rem;
    margin-bottom: 1rem;
}

.panel-title {
    color: var(--text);
    font-size: 1.25rem;
    font-weight: 900;
    margin-bottom: 0.45rem;
}

.insight {
    border-left: 5px solid var(--primary);
    background: linear-gradient(90deg, #eff6ff 0%, #ffffff 72%);
}

.timeline-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #f9fafb;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-top: 0.7rem;
    color: var(--text);
}

.learning-card {
    padding: 1.25rem 1.35rem;
    margin-bottom: 1rem;
    border-left: 6px solid var(--border);
}

.learning-card.completed {
    background: var(--success-soft);
    border-color: #86efac;
    border-left-color: var(--success);
}

.learning-card.started {
    background: #eff6ff;
    border-color: #93c5fd;
    border-left-color: var(--primary);
}

.learning-card.missed {
    background: #fff7ed;
    border-color: #fed7aa;
    border-left-color: var(--warning);
}

.roadmap-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.phase-title {
    color: var(--text);
    font-size: 1.25rem;
    font-weight: 900;
}

.status-pill, .concept-pill, .skill-pill {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.78rem;
    padding: 0.28rem 0.65rem;
    margin: 0.15rem 0.25rem 0.15rem 0;
}

.status-pill {
    background: var(--primary-soft);
    color: var(--primary);
}

.concept-pill {
    background: #f3f4f6;
    color: var(--muted);
}

.skill-pill {
    background: var(--success-soft);
    color: var(--success);
}

.lesson-panel {
    padding: 1.4rem;
    margin: 1rem 0;
}

.lesson-section {
    border-top: 1px solid var(--border);
    padding-top: 1rem;
    margin-top: 1rem;
}

.lesson-section:first-child {
    border-top: 0;
    padding-top: 0;
    margin-top: 0;
}

.lesson-section h3 {
    color: var(--text);
    font-size: 1.05rem;
    font-weight: 900;
    margin-bottom: 0.45rem;
}

.lesson-section p {
    color: var(--muted);
    line-height: 1.65;
}

.chat-row {
    display: flex;
    margin: 0.7rem 0;
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-bubble {
    max-width: 78%;
    border-radius: 18px;
    padding: 0.85rem 1rem;
    line-height: 1.55;
    border: 1px solid var(--border);
}

.chat-row.user .chat-bubble {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
    border-bottom-right-radius: 6px;
}

.chat-row.tutor .chat-bubble {
    background: #ffffff;
    color: var(--text);
    border-bottom-left-radius: 6px;
}

.chat-name {
    display: block;
    font-size: 0.75rem;
    font-weight: 900;
    opacity: 0.82;
    margin-bottom: 0.25rem;
}

.job-card {
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.job-top {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
}

.job-title {
    color: var(--text);
    font-size: 1.2rem;
    font-weight: 900;
}

.job-company {
    color: var(--muted);
    margin-top: 0.2rem;
}

.match-score {
    color: var(--success);
    font-weight: 900;
    white-space: nowrap;
}

hr {
    border-color: var(--border);
}

@media (max-width: 900px) {
    .top-nav {
        align-items: flex-start;
        flex-direction: column;
    }

    .brand {
        min-width: auto;
    }

    .stat-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .stat-grid {
        grid-template-columns: 1fr;
    }

    .hero {
        padding: 2.25rem 1rem;
    }

    .roadmap-head, .job-top {
        flex-direction: column;
    }

    .chat-bubble {
        max-width: 92%;
    }
}
</style>
""", unsafe_allow_html=True)


# ===========================================================
# HELPERS
# ===========================================================
def parse_skills(text):
    return [s.strip() for s in text.split(",") if s.strip()]


def safe_metric(metric, attr, default=0):
    try:
        return getattr(metric, attr, default)
    except Exception:
        return default


def escape(value):
    return html.escape(str(value))


def status_meta(status):
    if status == "TASK_COMPLETED":
        return "completed", "Completed", "✓"
    if status == "TASK_STARTED":
        return "started", "In Progress", "↗"
    if status == "TASK_MISSED":
        return "missed", "Needs Attention", "!"
    return "pending", "Ready", "•"


def chat_message(role, content):
    row_role = "user" if role == "user" else "tutor"
    name = "You" if role == "user" else "AI Tutor"
    st.markdown(
        f"""
        <div class="chat-row {row_role}">
            <div class="chat-bubble">
                <span class="chat-name">{name}</span>
                {escape(content)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_page_header(kicker, title, copy):
    st.markdown(
        f"""
        <div class="page-kicker">{escape(kicker)}</div>
        <div class="page-title">{escape(title)}</div>
        <div class="page-copy">{escape(copy)}</div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(icon, number, label, note, color="blue"):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-icon {color}">{escape(icon)}</div>
            <div class="stat-number">{escape(number)}</div>
            <div class="stat-label">{escape(label)}</div>
            <div class="stat-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_concepts(concepts):
    if not concepts:
        concepts = ["Core concepts"]
    return "".join(
        f'<span class="concept-pill">{escape(concept)}</span>'
        for concept in concepts
    )


# ===========================================================
# SIDEBAR
# ===========================================================
st.sidebar.markdown("## Build Your Plan")
st.sidebar.caption("Set the inputs for BridgeUp AI to generate your adaptive path.")

goal = st.sidebar.text_input(
    "Career Goal",
    "Backend Developer"
)

skills_input = st.sidebar.text_input(
    "Existing Skills",
    "Python"
)

weekly_hours = st.sidebar.slider(
    "Weekly Study Hours",
    1,
    40,
    10
)

run_btn = st.sidebar.button("Generate Learning Path", use_container_width=True)


# ===========================================================
# TOP NAVIGATION
# ===========================================================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

st.markdown(
    """
    <div class="top-nav">
        <div class="brand">
            <div class="brand-mark">B</div>
            <div>
                <div class="brand-title">BridgeUp AI</div>
                <div class="brand-subtitle">Adaptive learning platform</div>
            </div>
        </div>
        <div style="flex:1"></div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="nav-shell">', unsafe_allow_html=True)
st.radio(
    "Navigation",
    ["Dashboard", "Learning Journey", "Learn", "Career Opportunities"],
    key="page",
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)


# ===========================================================
# INIT SESSION
# ===========================================================
def init_session(result):

    if result is None:
        result = {}

    st.session_state.initialized = True

    st.session_state.session_id = result.get(
        "session_id",
        "demo-session"
    )

    st.session_state.strategy = result.get(
        "selected_strategy",
        "adaptive"
    )

    raw_tasks = result.get("tasks", [])

    tasks = []

    if not raw_tasks:

        fallback = [
            "Core Fundamentals",
            "Projects & Practice",
            "Advanced Concepts",
            "Career Preparation"
        ]

        for i, item in enumerate(fallback):

            raw_tasks.append({
                "task_id": f"task_{i}",
                "title": item,
                "concepts": [item],
                "level": "Beginner",
                "skill": goal
            })

    for i, t in enumerate(raw_tasks):

        if isinstance(t, dict):

            task_id = t.get(
                "task_id",
                f"task_{i}"
            )

            title = t.get(
                "title",
                f"Task {i+1}"
            )

            concepts = t.get(
                "concepts",
                []
            )

            level = t.get(
                "level",
                "Beginner"
            )

            skill = t.get(
                "skill",
                goal
            )

        else:

            task_id = getattr(
                t,
                "task_id",
                f"task_{i}"
            )

            title = getattr(
                t,
                "title",
                f"Task {i+1}"
            )

            concepts = getattr(
                t,
                "concepts",
                []
            )

            level = getattr(
                t,
                "level",
                "Beginner"
            )

            skill = getattr(
                t,
                "skill",
                goal
            )

        tasks.append({
            "task_id": task_id,
            "title": title,
            "concepts": concepts,
            "level": level,
            "skill": skill
        })

    st.session_state.tasks = tasks

    if "task_status" not in st.session_state:

        st.session_state.task_status = {
            t["task_id"]: "pending"
            for t in tasks
        }

    st.session_state.metric = result.get(
        "metric_snapshot"
    )

    st.session_state.jobs = result.get(
        "job_recommendations",
        []
    )

    st.session_state.timeline = []

    st.session_state.monitor = MonitoringAgent(
        base_path=Path("data/monitoring_logs")
    )


# ===========================================================
# UPDATE TASK STATUS
# ===========================================================
def update_task_status(task_id, event_type):

    try:

        monitor = st.session_state.monitor

        session_id = st.session_state.session_id

        now = datetime.utcnow().isoformat()

        monitor.collector.record_task_event({
            "event_type": event_type,
            "task_id": task_id,
            "session_id": session_id,
            "timestamp": now,
            "payload": {}
        })

        st.session_state.task_status[task_id] = event_type

        monitor.collector.build_session_snapshot(
            session_id=session_id,
            weekly_hours_allocated=weekly_hours,
            planned_days=5
        )

        metric = monitor.get_session_metrics(
            session_id
        )

        st.session_state.metric = metric

        if event_type == "TASK_COMPLETED":

            st.session_state.timeline.append(
                "Lesson completed successfully"
            )

        elif event_type == "TASK_STARTED":

            st.session_state.timeline.append(
                "Learning session started"
            )

        else:

            st.session_state.timeline.append(
                "BridgeUp noticed a missed learning activity"
            )

    except Exception:
        pass


# ===========================================================
# RUN BACKEND
# ===========================================================
if run_btn:

    with st.spinner(
        "Creating your personalized learning experience..."
    ):

        try:

            skills = parse_skills(skills_input)

            result = run_bridgeup(
                goal,
                skills,
                weekly_hours
            )

            init_session(result)

        except Exception as e:

            st.error(f"System error: {e}")
            st.stop()


if "initialized" not in st.session_state:
    st.markdown(
        """
        <section class="hero">
            <h1>From Learning to <span class="accent">Earning</span> with BridgeUp AI</h1>
            <p>
                Generate a personalized roadmap, learn with an AI tutor, track progress,
                and discover career opportunities from one clean learning workspace.
            </p>
        </section>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_stat_card("✓", "Plan", "Adaptive roadmap", "Built from your goals", "green")
    with c2:
        render_stat_card("AI", "Tutor", "Guided lessons", "Ask questions anytime", "blue")
    with c3:
        render_stat_card("%", "Jobs", "Career matches", "Aligned to your skills", "orange")

    st.info("Use the sidebar to generate your learning path.")
    st.stop()


# ===========================================================
# TUTOR STATE
# ===========================================================
if "tutor" not in st.session_state:
    st.session_state.tutor = LearningTutor()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "lesson_started" not in st.session_state:
    st.session_state.lesson_started = False

if "lesson_data" not in st.session_state:
    st.session_state.lesson_data = None


# ===========================================================
# DASHBOARD
# ===========================================================
if st.session_state.page == "Dashboard":

    render_page_header(
        "Dashboard",
        f"Welcome, Future {goal}",
        "Your personalized roadmap is ready. BridgeUp adapts the experience based on your progress and learning behavior."
    )

    metric = st.session_state.metric

    completion = safe_metric(
        metric,
        "completion_rate"
    )

    risk = safe_metric(
        metric,
        "dropoff_risk_score"
    )

    stability = safe_metric(
        metric,
        "stability_score"
    )

    tasks = st.session_state.tasks
    completed_tasks = sum(
        1 for task in tasks
        if st.session_state.task_status.get(task["task_id"]) == "TASK_COMPLETED"
    )
    total_tasks = max(len(tasks), 1)
    visible_completion = completion if completion else completed_tasks / total_tasks
    started_tasks = sum(
        1 for task in tasks
        if st.session_state.task_status.get(task["task_id"]) == "TASK_STARTED"
    )

    if risk > 0.3:
        risk_text = "Needs Balance"
        risk_note = "Try a lighter study pace"
    else:
        risk_text = "Healthy"
        risk_note = "Your workload looks sustainable"

    if stability > 0.5:
        consistency = "Strong"
        consistency_note = "Keep your rhythm"
    else:
        consistency = "Improving"
        consistency_note = "Start one more lesson this week"

    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        render_stat_card("✓", f"{completed_tasks}", f"of {total_tasks} Tasks", f"{visible_completion:.0%} Complete", "green")
    with s2:
        render_stat_card("↗", f"{started_tasks}", "Active Lessons", "Currently in progress", "blue")
    with s3:
        render_stat_card("⚖", risk_text, "Learning Balance", risk_note, "orange")
    with s4:
        render_stat_card("★", consistency, "Study Consistency", consistency_note, "blue")
    st.markdown('</div>', unsafe_allow_html=True)

    st.progress(min(max(visible_completion, 0), 1))

    insight = "Continue completing lessons to strengthen your learning profile."
    if visible_completion > 0.6:
        insight = "You're progressing consistently. Advanced concepts are being unlocked."
    elif risk > 0.3:
        insight = "Your recent activity suggests moderate learning fatigue. Keep the plan steady and manageable."

    st.markdown(
        f"""
        <div class="panel insight">
            <div class="panel-title">AI Learning Insights</div>
            <p>{escape(insight)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Recent Learning Activity</div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.timeline:
        for step in st.session_state.timeline[-5:]:
            st.markdown(
                f'<div class="timeline-item"><span class="status-pill">Update</span><span>{escape(step)}</span></div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="timeline-item"><span class="status-pill">Ready</span><span>Your learning activity will appear here.</span></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ===========================================================
# LEARNING JOURNEY
# ===========================================================
elif st.session_state.page == "Learning Journey":

    render_page_header(
        "Learning Journey",
        "Your Adaptive Learning Path",
        "Move through each phase like a guided course. Mark progress as you learn so BridgeUp can keep your plan current."
    )

    tasks = st.session_state.tasks

    if not tasks:
        st.info("No learning tasks available.")
        st.stop()

    completed_tasks = sum(
        1 for task in tasks
        if st.session_state.task_status.get(task["task_id"]) == "TASK_COMPLETED"
    )
    st.progress(completed_tasks / max(len(tasks), 1))

    for i, task in enumerate(tasks, 1):

        status = st.session_state.task_status[
            task["task_id"]
        ]

        card_class, status_label, status_icon = status_meta(status)

        st.markdown(
            f"""
            <div class="learning-card {card_class}">
                <div class="roadmap-head">
                    <div>
                        <span class="status-pill">Phase {i}</span>
                        <span class="skill-pill">{escape(task['level'])}</span>
                        <div class="phase-title">{escape(task['title'])}</div>
                        <p>{escape(task['skill'])}</p>
                    </div>
                    <span class="status-pill">{escape(status_icon)} {escape(status_label)}</span>
                </div>
                <div>{render_concepts(task["concepts"])}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 1, 1])

        if col1.button(
            "Complete",
            key=f"c_{task['task_id']}",
            use_container_width=True
        ):

            update_task_status(
                task["task_id"],
                "TASK_COMPLETED"
            )

            st.rerun()

        if col2.button(
            "Learning",
            key=f"p_{task['task_id']}",
            use_container_width=True
        ):

            update_task_status(
                task["task_id"],
                "TASK_STARTED"
            )

            st.rerun()

        if col3.button(
            "Missed",
            key=f"m_{task['task_id']}",
            use_container_width=True
        ):

            update_task_status(
                task["task_id"],
                "TASK_MISSED"
            )

            st.rerun()


# ===========================================================
# LEARN
# ===========================================================
elif st.session_state.page == "Learn":

    tasks = st.session_state.tasks

    titles = [t["title"] for t in tasks]

    render_page_header(
        "Learn",
        "AI Tutor Workspace",
        "Start a lesson, review the generated explanation, and ask follow-up questions without leaving your learning flow."
    )

    selected = st.selectbox(
        "Choose a lesson",
        titles
    )

    task = next(
        t for t in tasks
        if t["title"] == selected
    )

    st.markdown(
        f"""
        <div class="lesson-panel">
            <span class="status-pill">Current Lesson</span>
            <div class="phase-title">{escape(task['title'])}</div>
            <p>{escape(task['skill'])} · {escape(task['level'])}</p>
            <div>{render_concepts(task["concepts"])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.lesson_started:

        if st.button("Start Learning", use_container_width=True):

            try:

                lesson = (
                    st.session_state.tutor
                    .generate_contextual_lesson(
                        task_title=task["title"],
                        skill=task["skill"],
                        level=task["level"]
                    )
                )

            except Exception:

                lesson = type("Lesson", (), {

                    "explanation":
                        f"Learning {task['title']}",

                    "example":
                        "Example unavailable",

                    "practice_task":
                        "Practice this lesson",

                    "follow_up_question":
                        "What did you understand?"
                })()

            st.session_state.lesson_data = lesson
            st.session_state.lesson_started = True

            st.rerun()

    if st.session_state.lesson_started:

        lesson = st.session_state.lesson_data

        st.markdown(
            f"""
            <div class="lesson-panel">
                <div class="lesson-section">
                    <h3>Explanation</h3>
                    <p>{escape(lesson.explanation)}</p>
                </div>
                <div class="lesson-section">
                    <h3>Practice Task</h3>
                    <p>{escape(lesson.practice_task)}</p>
                </div>
                <div class="lesson-section">
                    <h3>Reflection</h3>
                    <p>{escape(lesson.follow_up_question)}</p>
                </div>
                <div class="lesson-section">
                    <h3>AI Hint</h3>
                    <p>Focus on understanding concepts before memorizing syntax.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Example")
        st.code(lesson.example)

        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">AI Tutor</div>
            """,
            unsafe_allow_html=True
        )

        if not st.session_state.chat_history:
            st.markdown(
                '<div class="timeline-item"><span class="status-pill">Tutor</span><span>Ask anything about this lesson.</span></div>',
                unsafe_allow_html=True
            )

        for msg in st.session_state.chat_history:

            chat_message(
                msg["role"],
                msg["content"]
            )

        st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.text_input(
            "Ask your AI tutor anything..."
        )

        col1, col2 = st.columns(2)

        if col1.button("Send", use_container_width=True) and user_input:

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            try:

                res = st.session_state.tutor.chat(
                    user_input=user_input,
                    skill=task["skill"],
                    level=task["level"],
                    goal=task["title"]
                )

                if isinstance(res, dict):
                    reply = res.get(
                        "message",
                        "Let's continue learning."
                    )

                else:
                    reply = str(res)

            except Exception:

                reply = (
                    "Let's continue learning together."
                )

            st.session_state.chat_history.append({
                "role": "tutor",
                "content": reply
            })

            st.rerun()

        if col2.button("End Session", use_container_width=True):

            st.session_state.lesson_started = False
            st.session_state.lesson_data = None
            st.session_state.chat_history = []

            st.rerun()

        if st.button("Lesson Completed", use_container_width=True):

            update_task_status(
                task["task_id"],
                "TASK_COMPLETED"
            )

            st.session_state.lesson_started = False
            st.session_state.lesson_data = None
            st.session_state.chat_history = []

            st.success(
                "Great progress! Your learning path has been updated."
            )

            st.rerun()


# ===========================================================
# CAREER OPPORTUNITIES
# ===========================================================
elif st.session_state.page == "Career Opportunities":

    render_page_header(
        "Career Opportunities",
        "Career Matches for Your Path",
        "Review roles that match your goal and current skills. BridgeUp keeps the recommendations focused on what you are learning."
    )

    jobs = st.session_state.jobs

    skills = parse_skills(skills_input)

    def calculate_match(title):

        score = 65

        title_lower = title.lower()

        keywords = [goal.lower()] + [
            s.lower() for s in skills
        ]

        for k in keywords:

            if k in title_lower:
                score += 8

        return min(score, 95)

    filtered_jobs = []

    for job in jobs:

        if isinstance(job, dict):

            title = job.get("title", "Role")
            company = job.get("company", "Company")
            link = job.get("link", "#")

        else:

            title = getattr(job, "title", "Role")
            company = getattr(job, "company", "Company")
            link = getattr(job, "link", "#")

        title_lower = title.lower()
        goal_terms = [term for term in goal.lower().replace("/", " ").split() if len(term) > 2]
        skill_terms = [skill.lower() for skill in skills]

        if (
            goal.lower() in title_lower
            or any(term in title_lower for term in goal_terms)
            or any(skill in title_lower for skill in skill_terms)
        ):

            filtered_jobs.append(
                (title, company, link)
            )

    if not filtered_jobs:

        filtered_jobs = [
            (
                f"Junior {goal}",
                "Tech Company",
                "#"
            ),
            (
                f"{goal} Intern",
                "Startup",
                "#"
            ),
            (
                f"Associate {goal}",
                "Product Company",
                "#"
            )
        ]

    for title, company, link in filtered_jobs:

        score = calculate_match(title)
        relevant_skills = skills[:3] if skills else [goal]
        skill_markup = "".join(
            f'<span class="skill-pill">{escape(skill)}</span>'
            for skill in relevant_skills
        )

        st.markdown(
            f"""
            <div class="job-card">
                <div class="job-top">
                    <div>
                        <div class="job-title">{escape(title)}</div>
                        <div class="job-company">{escape(company)}</div>
                    </div>
                    <div class="match-score">{score}% match</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(score / 100)
        st.markdown(skill_markup, unsafe_allow_html=True)

        if link != "#":

            st.markdown(
                f"[Apply Now]({link})"
            )
