import requests
import streamlit as st


st.set_page_config(page_title="Wanderly", page_icon="🌴", layout="centered")

BACKEND_URL = "http://localhost:8000"
EXAMPLES = [
    "5 days in Goa for two people",
    "A 4-day budget trip to Jaipur",
    "A relaxed weekend in Bali",
]


def backend_is_ready() -> bool:
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=2).ok
    except requests.RequestException:
        return False


def get_plan(question: str, response_length: str) -> str:
    response = requests.post(
        f"{BACKEND_URL}/query",
        json={"question": question, "response_length": response_length},
        timeout=300,
    )
    if not response.ok:
        try:
            message = response.json().get("error", response.text)
        except ValueError:
            message = response.text
        raise RuntimeError(message)
    answer = response.json().get("answer")
    if not answer:
        raise RuntimeError("The planner returned an empty response.")
    return answer


st.markdown(
    """
    <style>
    .stApp { background: #f4f1eb; color: #263832; }
    .block-container { max-width: 900px; padding: 3.5rem 2rem 4rem; }
    .brand { color: #1f7668; font-size: .78rem; font-weight: 800; letter-spacing: .18em; }
    .hero h1 { color: #183b35; font-size: clamp(2.2rem, 6vw, 3.8rem); line-height: 1.05; margin: .55rem 0 .7rem; }
    .hero p { color: #687670; font-size: 1.08rem; max-width: 600px; margin-bottom: 1.6rem; }
    .status { display: inline-block; color: #1f7668; background: #e2f1e9; border-radius: 999px; padding: .35rem .75rem; font-size: .82rem; font-weight: 700; }
    .status.offline { color: #9c542b; background: #f9e6d7; }
    .result { background: #fffdf9; border: 1px solid #e4ded3; border-top: 4px solid #d27b38; border-radius: 14px; padding: 1.4rem 1.6rem; box-shadow: 0 10px 24px rgba(62, 54, 42, .07); }
    div[data-testid="stTextArea"] textarea { border: 1px solid #c9d6ce; border-radius: 12px; background: #fffdf9; }
    div[data-testid="stTextArea"] textarea:focus { border-color: #1f7668; box-shadow: 0 0 0 2px rgba(31, 118, 104, .16); }
    div.stButton > button, div.stButton > button p, div.stDownloadButton > button, div.stDownloadButton > button p { border-radius: 10px; border: 1px solid #b9cbc1; color: #205247 !important; background: #fffdf9; font-weight: 700; transition: all .18s ease; }
    div.stButton > button:hover, div.stButton > button:hover p, div.stDownloadButton > button:hover, div.stDownloadButton > button:hover p { color: #fffdf9 !important; background: #1f7668; border-color: #1f7668; transform: translateY(-2px); box-shadow: 0 7px 16px rgba(31, 118, 104, .2); }
    div[data-testid="stFormSubmitButton"] button, div[data-testid="stFormSubmitButton"] button p { color: #fffdf9 !important; background: #1f7668; border-color: #1f7668; }
    div[data-testid="stFormSubmitButton"] button:hover, div[data-testid="stFormSubmitButton"] button:hover p { color: #fffdf9 !important; background: #185e53; border-color: #185e53; }
    .suggestion { color: #718078; font-size: .9rem; margin-top: 1.5rem; }
    div[role="radiogroup"] { gap: .5rem; }
    div[role="radiogroup"] label { border: 1px solid #c9d6ce; border-radius: 10px; padding: .35rem .7rem; background: #fffdf9; }
    div[role="radiogroup"] label p, div[role="radiogroup"] label span { color: #205247 !important; opacity: 1 !important; font-weight: 700 !important; }
    div[role="radiogroup"] label:has(input:checked) { background: #dcefe8; border-color: #1f7668; }
    .response-label { color: #183b35; font-size: .92rem; font-weight: 800; margin: .8rem 0 .35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "plan" not in st.session_state:
    st.session_state.plan = ""
if "question" not in st.session_state:
    st.session_state.question = ""

st.markdown('<div class="brand">WANDERLY · AI TRIP PLANNER</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
        <h1>Plan a trip worth remembering.</h1>
        <p>Tell us where you want to go, how long you have, and the kind of experience you want.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

ready = backend_is_ready()
status_text = "● Ready to plan" if ready else "○ Start the backend to begin"
status_class = "" if ready else " offline"
st.markdown(f'<span class="status{status_class}">{status_text}</span>', unsafe_allow_html=True)

with st.form("planner"):
    question = st.text_area(
        "Your trip",
        value=st.session_state.question,
        placeholder="e.g. Plan a 5-day Goa trip for two people with beaches and local food.",
        height=120,
    )
    st.markdown('<div class="response-label">Response style</div>', unsafe_allow_html=True)
    response_length = st.radio(
        "Response style",
        options=["short", "standard", "detailed"],
        index=1,
        format_func=lambda value: {
            "short": "Quick",
            "standard": "Balanced",
            "detailed": "Well explained",
        }[value],
        horizontal=True,
        label_visibility="collapsed",
    )
    left, right = st.columns([1, 1])
    with left:
        submitted = st.form_submit_button("Create itinerary", type="primary", use_container_width=True)
    with right:
        cleared = st.form_submit_button("Clear", use_container_width=True)

if cleared:
    st.session_state.question = ""
    st.session_state.plan = ""
    st.rerun()

if submitted:
    question = question.strip()
    if not question:
        st.warning("Add a destination and trip length first.")
    else:
        with st.spinner("Planning your trip..."):
            try:
                st.session_state.plan = get_plan(question, response_length)
                st.session_state.question = question
            except (requests.RequestException, RuntimeError) as error:
                st.error(f"Could not create the itinerary: {error}")

if not st.session_state.plan:
    st.markdown('<div class="suggestion">Need inspiration?</div>', unsafe_allow_html=True)
    example_columns = st.columns(len(EXAMPLES))
    for column, example in zip(example_columns, EXAMPLES):
        with column:
            if st.button(example, use_container_width=True):
                st.session_state.question = example
                st.rerun()
else:
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown("### Your itinerary")
    st.markdown(st.session_state.plan)
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        "Download itinerary",
        data=f"# Wanderly itinerary\n\n{st.session_state.plan}",
        file_name="wanderly-itinerary.md",
        mime="text/markdown",
    )
    st.caption("Check current prices, opening hours, weather, and travel requirements before booking.")
