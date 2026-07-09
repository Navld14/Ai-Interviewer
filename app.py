import streamlit as st
import anthropic
import json
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interviewer 💼",
    page_icon="💼",
    layout="centered"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p { color: #888; font-size: 1rem; margin-top: -6px; }

.question-card {
    background: linear-gradient(135deg, #0a0a1a, #0f0f2e);
    border: 1px solid #6366f133;
    border-left: 3px solid #6366f1;
    border-radius: 0 14px 14px 0;
    padding: 20px 24px;
    margin: 12px 0;
}
.question-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 8px;
}
.question-text {
    color: #e2e8f0;
    font-size: 1.05rem;
    line-height: 1.7;
}

.feedback-card {
    background: #0a1a0a;
    border: 1px solid #22c55e33;
    border-radius: 14px;
    padding: 20px;
    margin: 12px 0;
}
.feedback-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #22c55e;
    margin-bottom: 8px;
}

.score-pill {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.stat-box {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-value { font-size: 2rem; font-weight: 700; }
.stat-label { font-size: 0.65rem; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

.progress-bar-bg {
    background: #1a1a1a;
    border-radius: 999px;
    height: 6px;
    margin: 8px 0 16px 0;
}
.progress-bar-fill {
    height: 6px;
    border-radius: 999px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.report-item {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
ROLES = {
    "🧑‍💻 Software Engineer": "software engineering, data structures, algorithms, system design, OOP",
    "🤖 ML Engineer": "machine learning, deep learning, model deployment, MLOps, Python, PyTorch",
    "📊 Data Scientist": "statistics, data analysis, pandas, SQL, machine learning, visualization",
    "🎨 Frontend Developer": "HTML, CSS, JavaScript, React, responsive design, web performance",
    "⚙️ Backend Developer": "APIs, databases, system design, scalability, Node.js or Python",
    "📦 Product Manager": "product thinking, roadmaps, stakeholder management, metrics, user stories",
    "☁️ DevOps Engineer": "CI/CD, Docker, Kubernetes, cloud platforms, infrastructure as code",
}

LEVELS = {
    "🟢 Junior (0-2 years)": "junior",
    "🟡 Mid-Level (2-5 years)": "mid",
    "🔴 Senior (5+ years)": "senior"
}

TOTAL_QUESTIONS = 5

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_question(role, level, asked_questions, question_num):
    client = anthropic.Anthropic()
    asked = "\n".join([f"- {q}" for q in asked_questions]) if asked_questions else "None yet"

    prompt = f"""You are a strict but fair technical interviewer at a top tech company.

Role: {role}
Level: {level}
Question number: {question_num} of {TOTAL_QUESTIONS}
Questions already asked:
{asked}

Generate ONE interview question. Mix technical and behavioral questions across the interview.
Early questions (1-2) should be easier, later ones (4-5) harder.
Do NOT repeat similar questions to ones already asked.

Respond with ONLY the question text. No preamble, no numbering, no explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def evaluate_answer(role, level, question, answer):
    client = anthropic.Anthropic()

    prompt = f"""You are a strict but fair technical interviewer evaluating a candidate's answer.

Role: {role}
Level: {level}
Question: {question}
Candidate's Answer: {answer}

Evaluate the answer and respond ONLY with valid JSON (no markdown, no preamble):
{{
  "score": <integer 1-10>,
  "verdict": "<one of: Excellent | Good | Average | Below Average | Poor>",
  "strength": "<one specific thing they did well in 1 sentence>",
  "improvement": "<one specific thing they should improve in 1 sentence>",
  "ideal_points": "<2-3 key points a strong answer would include, comma separated>"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_final_report(role, level, qa_pairs):
    client = anthropic.Anthropic()

    qa_text = "\n\n".join([
        f"Q{i+1}: {qa['question']}\nA: {qa['answer']}\nScore: {qa['score']}/10"
        for i, qa in enumerate(qa_pairs)
    ])

    prompt = f"""You are a senior interviewer writing a final assessment report.

Role: {role}
Level: {level}

Interview transcript:
{qa_text}

Write a final report as JSON (no markdown, no preamble):
{{
  "overall_score": <integer 1-100>,
  "verdict": "<one of: Strong Hire | Hire | Maybe | No Hire | Strong No Hire>",
  "verdict_color": "<one of: #22c55e | #86efac | #f59e0b | #ef4444 | #991b1b>",
  "summary": "<2-3 sentence overall assessment of the candidate>",
  "top_strength": "<their biggest strength observed across the interview>",
  "top_weakness": "<their biggest area for improvement>",
  "recommendation": "<specific advice for this candidate going forward in 1-2 sentences>"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def score_color(score):
    if score >= 8: return "#22c55e"
    if score >= 6: return "#f59e0b"
    return "#ef4444"


# ── Session init ───────────────────────────────────────────────────────────────
def init():
    defaults = {
        "stage": "setup",       # setup | interview | feedback | report
        "role": None,
        "level": None,
        "question_num": 0,
        "current_question": None,
        "qa_pairs": [],
        "asked_questions": [],
        "current_feedback": None,
        "final_report": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <h1>💼 AI Interviewer</h1>
    <p>Practice interviews with an AI that actually evaluates you.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# STAGE 1 — Setup
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "setup":
    st.markdown("### 🎯 Configure Your Interview")

    role_choice = st.selectbox("Select Role", list(ROLES.keys()))
    level_choice = st.selectbox("Select Level", list(LEVELS.keys()))

    st.info(f"You'll be asked **{TOTAL_QUESTIONS} questions** — a mix of technical and behavioral. Each answer is scored 1–10 with detailed feedback.")

    if st.button("Start Interview →", type="primary", use_container_width=True):
        st.session_state.role = role_choice
        st.session_state.level = LEVELS[level_choice]
        st.session_state.stage = "interview"
        st.session_state.question_num = 1

        with st.spinner("Preparing your first question... 🎤"):
            q = get_question(role_choice, LEVELS[level_choice], [], 1)
        st.session_state.current_question = q
        st.session_state.asked_questions = [q]
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STAGE 2 — Interview
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "interview":
    # Progress
    progress = (st.session_state.question_num - 1) / TOTAL_QUESTIONS
    st.markdown(f"**Question {st.session_state.question_num} of {TOTAL_QUESTIONS}** — {st.session_state.role} · {st.session_state.level.title()}")
    st.markdown(f"""
    <div class='progress-bar-bg'>
        <div class='progress-bar-fill' style='width:{progress*100:.0f}%'></div>
    </div>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"""
    <div class='question-card'>
        <div class='question-label'>🎤 Interviewer</div>
        <div class='question-text'>{st.session_state.current_question}</div>
    </div>
    """, unsafe_allow_html=True)

    # Answer input
    answer = st.text_area(
        "Your Answer",
        placeholder="Type your answer here... be thorough, use examples where possible.",
        height=160,
        key=f"answer_{st.session_state.question_num}"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        submit = st.button("Submit Answer →", type="primary", use_container_width=True)
    with col2:
        skip = st.button("Skip ⏭️", use_container_width=True)

    if submit or skip:
        final_answer = answer.strip() if (submit and answer.strip()) else "I'm not sure about this one."

        with st.spinner("Evaluating your answer... 🧠"):
            feedback = evaluate_answer(
                st.session_state.role,
                st.session_state.level,
                st.session_state.current_question,
                final_answer
            )

        st.session_state.qa_pairs.append({
            "question": st.session_state.current_question,
            "answer": final_answer,
            **feedback
        })
        st.session_state.current_feedback = feedback
        st.session_state.stage = "feedback"
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STAGE 3 — Feedback
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "feedback":
    fb = st.session_state.current_feedback
    qa = st.session_state.qa_pairs[-1]

    st.markdown(f"**Question {st.session_state.question_num} of {TOTAL_QUESTIONS}** · Feedback")

    # Question recap
    st.markdown(f"""
    <div class='question-card'>
        <div class='question-label'>Question</div>
        <div class='question-text'>{qa['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Score
    color = score_color(fb['score'])
    st.markdown(f"""
    <div class='feedback-card'>
        <div class='feedback-label'>📊 Evaluation</div>
        <span class='score-pill' style='background:{color}22; color:{color}; border:1px solid {color}44'>
            {fb['score']}/10 — {fb['verdict']}
        </span>
        <div style='margin-top:12px'>
            <div style='color:#86efac; font-size:0.85rem; margin-bottom:6px'>✅ <b>Strength:</b> {fb['strength']}</div>
            <div style='color:#fca5a5; font-size:0.85rem; margin-bottom:6px'>⚠️ <b>Improve:</b> {fb['improvement']}</div>
            <div style='color:#94a3b8; font-size:0.85rem'>💡 <b>Key points to cover:</b> {fb['ideal_points']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Next
    is_last = st.session_state.question_num >= TOTAL_QUESTIONS

    if st.button(
        "View Final Report 📋" if is_last else f"Next Question → ({st.session_state.question_num + 1}/{TOTAL_QUESTIONS})",
        type="primary",
        use_container_width=True
    ):
        if is_last:
            with st.spinner("Generating your final report... 📋"):
                report = generate_final_report(
                    st.session_state.role,
                    st.session_state.level,
                    st.session_state.qa_pairs
                )
            st.session_state.final_report = report
            st.session_state.stage = "report"
        else:
            next_num = st.session_state.question_num + 1
            with st.spinner("Loading next question... 🎤"):
                q = get_question(
                    st.session_state.role,
                    st.session_state.level,
                    st.session_state.asked_questions,
                    next_num
                )
            st.session_state.current_question = q
            st.session_state.asked_questions.append(q)
            st.session_state.question_num = next_num
            st.session_state.current_feedback = None
            st.session_state.stage = "interview"
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STAGE 4 — Final Report
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "report":
    report = st.session_state.final_report
    scores = [qa['score'] for qa in st.session_state.qa_pairs]
    avg_score = sum(scores) / len(scores)

    st.markdown("### 📋 Interview Complete — Final Report")

    # Overall
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='stat-box'>
            <div class='stat-value' style='color:#6366f1'>{report['overall_score']}</div>
            <div class='stat-label'>Overall Score /100</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='stat-box'>
            <div class='stat-value' style='color:{report["verdict_color"]}'>{avg_score:.1f}</div>
            <div class='stat-label'>Avg Answer Score /10</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='stat-box'>
            <div class='stat-value' style='color:{report["verdict_color"]}; font-size:1rem; padding-top:8px'>{report['verdict']}</div>
            <div class='stat-label'>Hiring Verdict</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Summary
    st.markdown(f"""
    <div style='background:#111; border:1px solid #222; border-radius:14px; padding:20px; margin-bottom:16px'>
        <div style='font-size:0.7rem; color:#555; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px'>Assessment</div>
        <p style='color:#cbd5e1; line-height:1.7; margin:0'>{report['summary']}</p>
        <div style='margin-top:14px'>
            <div style='color:#86efac; font-size:0.85rem; margin-bottom:6px'>💪 <b>Top Strength:</b> {report['top_strength']}</div>
            <div style='color:#fca5a5; font-size:0.85rem; margin-bottom:6px'>📈 <b>Top Weakness:</b> {report['top_weakness']}</div>
            <div style='color:#93c5fd; font-size:0.85rem'>🎯 <b>Recommendation:</b> {report['recommendation']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Per-question breakdown
    st.markdown("#### 📊 Question Breakdown")
    for i, qa in enumerate(st.session_state.qa_pairs):
        color = score_color(qa['score'])
        with st.expander(f"Q{i+1} — Score: {qa['score']}/10 · {qa['verdict']}"):
            st.markdown(f"**Question:** {qa['question']}")
            st.markdown(f"**Your Answer:** {qa['answer']}")
            st.markdown(f"**Feedback:** {qa['strength']} | {qa['improvement']}")

    st.markdown("---")

    if st.button("🔄 Start New Interview", use_container_width=True, type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center; color:#333; font-size:0.8rem'>Built with Python · Claude API · Streamlit</p>", unsafe_allow_html=True)
