import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(page_title="ResearchMind", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* Reset and base */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {
    padding-top: 3rem !important;
    max-width: 1200px;
}

/* Global Dark Theme with Radial Gradient */
.stApp {
    background: radial-gradient(circle at 50% 10%, #1e1e28 0%, #0d0d12 40%, #050508 100%);
    background-attachment: fixed;
    color: #ffffff;
}

/* Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Header */
.title-container {
    text-align: center;
    margin-bottom: 4rem;
    animation: fadeIn 1s ease-in-out;
}
.small-title {
    color: #ff7b00;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.main-title {
    font-size: 4.5rem;
    font-weight: 900;
    margin: -10px 0 15px 0;
    letter-spacing: -1px;
}
.main-title span.white { color: #ffffff; }
.main-title span.orange { color: #ff7b00; }
.subtitle {
    color: #8a8a93;
    font-size: 1.05rem;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 123, 0, 0.4); }
    70% { box-shadow: 0 0 0 15px rgba(255, 123, 0, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 123, 0, 0); }
}

/* Labels */
.section-label {
    color: #ff7b00;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* Pipeline styles */
.pipeline-card {
    background-color: rgba(20, 20, 25, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s ease;
}
.pipeline-card.running {
    border-color: #ff7b00;
    animation: pulse 2s infinite;
}
.pipeline-card.done {
    border-color: rgba(34, 197, 94, 0.5);
    background-color: rgba(20, 25, 20, 0.6);
}
.card-left {
    display: flex;
    flex-direction: column;
}
.card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 12px;
}
.card-num {
    color: #ff7b00;
    font-size: 0.95rem;
    font-weight: 800;
}
.card-desc {
    color: #8a8a93;
    font-size: 0.85rem;
    margin-top: 6px;
}
.card-status {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #666;
    text-transform: uppercase;
}
.pipeline-card.running .card-status { color: #ff7b00; }
.pipeline-card.done .card-status { color: #22c55e; }

/* Overriding Streamlit Text Input */
.stTextInput > div > div > input {
    background-color: rgba(20, 20, 25, 0.7) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    padding: 12px 15px !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff7b00 !important;
    box-shadow: 0 0 0 1px #ff7b00 !important;
}

/* Primary Button (Run Research Pipeline) */
button[kind="primary"], button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #ff9d00 0%, #ff5e00 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 0 !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(255, 94, 0, 0.4) !important;
}

/* Secondary Buttons (TRY pills) */
button[kind="secondary"], button[data-testid="baseButton-secondary"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #a0a0a5 !important;
    padding: 6px 16px !important;
    font-size: 0.8rem !important;
    border-radius: 20px !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.5 !important;
}
button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {
    border-color: #ff7b00 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <div class="small-title">Multi-Agent AI System</div>
    <div class="main-title"><span class="white">Research</span><span class="orange">Mind</span></div>
    <div class="subtitle">Four specialized AI agents collaborate — searching, scraping, writing, and critiquing — to deliver a polished research report on any topic.</div>
</div>
""", unsafe_allow_html=True)

# Session State Initialization
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'report' not in st.session_state:
    st.session_state.report = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'topic_key' not in st.session_state:
    st.session_state.topic_key = ""

def set_topic(t):
    st.session_state.topic_key = t

col1, spacer, col2 = st.columns([1.2, 0.2, 1.2])

with col1:
    st.markdown('<div class="section-label">RESEARCH TOPIC</div>', unsafe_allow_html=True)
    st.text_input("topic", placeholder="e.g. Quantum computing breakthroughs in 2025", label_visibility="collapsed", key="topic_key")
    
    # Use type="primary" to apply the orange gradient styling specifically to this button
    if st.button("⚡ Run Research Pipeline", key="run_btn", type="primary", use_container_width=True):
        if st.session_state.topic_key.strip():
            st.session_state.pipeline_running = True
            st.session_state.report = None
            st.session_state.feedback = None
        else:
            st.error("Please enter a topic.")

    st.markdown('<div style="margin-top:30px; font-size:0.75rem; color:#8a8a93; font-weight:600; letter-spacing:1px; margin-bottom:10px;">TRY &darr;</div>', unsafe_allow_html=True)
    
    # Try buttons use default type="secondary" for the pill styling
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.button("LLM agents 2025", on_click=set_topic, args=("LLM agents 2025",), use_container_width=True)
    with c2:
        st.button("CRISPR gene editing", on_click=set_topic, args=("CRISPR gene editing",), use_container_width=True)
    with c3:
        st.button("Fusion energy progress", on_click=set_topic, args=("Fusion energy progress",), use_container_width=True)

with col2:
    st.markdown('<h3 style="margin-bottom:20px; margin-top:0; font-weight:800; font-size:1.4rem;">Pipeline</h3>', unsafe_allow_html=True)
    pipeline_placeholder = st.empty()

def render_pipeline(current_step):
    def get_class_and_status(my_step):
        if current_step > my_step:
            return "done", "DONE ✓"
        elif current_step == my_step:
            return "running", "RUNNING..."
        else:
            return "", "WAITING"

    steps = [
        {"num": "01", "name": "Search Agent", "desc": "Gathers recent web information"},
        {"num": "02", "name": "Reader Agent", "desc": "Scrapes & extracts deep content"},
        {"num": "03", "name": "Writer Chain", "desc": "Drafts the full research report"},
        {"num": "04", "name": "Critic Chain", "desc": "Reviews & scores the report"}
    ]

    html = ""
    for i, step in enumerate(steps, 1):
        c, s = get_class_and_status(i)
        html += f"""
        <div class="pipeline-card {c}">
            <div class="card-left">
                <div class="card-title"><span class="card-num">{step['num']}</span> {step['name']}</div>
                <div class="card-desc">{step['desc']}</div>
            </div>
            <div class="card-status">{s}</div>
        </div>
        """
    pipeline_placeholder.markdown(html, unsafe_allow_html=True)

if st.session_state.pipeline_running:
    state = {}
    topic = st.session_state.topic_key
    
    # Step 1
    render_pipeline(1)
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content
    
    # Step 2
    render_pipeline(2)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state['scraped_content'] = reader_result['messages'][-1].content
    
    # Step 3
    render_pipeline(3)
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    
    # Step 4
    render_pipeline(4)
    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })
    
    # Finished
    st.session_state.report = state["report"]
    st.session_state.feedback = state["feedback"]
    st.session_state.pipeline_running = False
    st.rerun()

else:
    if st.session_state.report:
        render_pipeline(5)
        st.markdown("---")
        st.markdown("<h3 style='color: white;'>📄 Final Research Report</h3>", unsafe_allow_html=True)
        st.markdown(f'<div style="background:rgba(20,20,25,0.6); padding:25px; border-radius:12px; border-left:5px solid #ff7b00; margin-bottom:25px; line-height: 1.6; color: #eee; backdrop-filter: blur(10px);">{st.session_state.report}</div>', unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: white;'>🧐 Critic Feedback</h3>", unsafe_allow_html=True)
        st.markdown(f'<div style="background:rgba(20,20,25,0.6); padding:25px; border-radius:12px; border-left:5px solid #22c55e; line-height: 1.6; color: #eee; backdrop-filter: blur(10px);">{st.session_state.feedback}</div>', unsafe_allow_html=True)
    else:
        render_pipeline(0)