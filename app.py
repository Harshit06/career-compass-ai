import streamlit as st
import google.generativeai as genai
import json
import requests
import time
from streamlit_lottie import st_lottie
from streamlit_card import card

# 1. Page Configuration
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide"
)

# 2. API Configuration via Secrets
# In Streamlit Cloud: Settings -> Secrets -> GOOGLE_API_KEY = "your_key"
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key! Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. UI Styling
def add_animated_background():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(-45deg, #0E1117, #1A1C23, #2D1B4E, #0E1117);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        </style>
    """, unsafe_allow_html=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# 4. Core AI Logic
def get_gemini_response(education, skills, interests, goals):
    # Set to 2.5 as requested
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a Career Mentor. Analyze this profile:
    - Education: {education}
    - Current Skills: {skills}
    - Interests: {interests}
    - Career Goals: {goals}

    Return ONLY a valid JSON object. No intro text, no backticks.
    Format:
    {{
      "Career Paths": [{{"role": "Title", "demand": "High", "avg_salary": "Range", "reason": "Why"}}],
      "Skills to Learn": [{{"name": "Skill", "type": "Technical/Soft", "resources": ["Source"]}}],
      "Learning Roadmap": {{"Short Term": ["Step 1"], "Long Term": ["Step 2"]}},
      "Projects": {{"Beginner": ["P1"], "Advanced": ["P2"]}},
      "Opportunities": [{{"platform": "Name", "role": "Type", "skill_gap": "Gap"}}],
      "Motivation": "Quote"
    }}
    """
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Handle case where model returns markdown blocks
    if "json" in text:
        text = text.split("json")[1].split("")[0].strip()
    elif "" in text:
        text = text.split("")[1].split("")[0].strip()
        
    return text

# --- App Layout ---
add_animated_background()

lottie_json = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_json:
    st_lottie(lottie_json, height=180, key="main_anim")

st.title("🧭 Career Compass AI")
st.write("Navigating your professional future with Gemini 2.5")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        education = st.text_input("🎓 Your Education", placeholder="e.g. B.Tech Computer Science")
        skills = st.text_input("💻 Current Skills", placeholder="e.g. Java, Python, SQL")
    with c2:
        interests = st.text_input("🎨 Your Interests", placeholder="e.g. App Dev, AI, Design")
        goals = st.text_input("🎯 Your Goals", placeholder="e.g. Work at a Tech Giant")

if st.button("🚀 Generate My Career Path", use_container_width=True):
    if all([education, skills, interests, goals]):
        with st.spinner("Processing your path..."):
            try:
                res_text = get_gemini_response(education, skills, interests, goals)
                data = json.loads(res_text)
                
                st.balloons()
                
                # --- Career Display ---
                st.header("🎯 Recommended Paths")
                paths = data.get("Career Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                for i, path in enumerate(paths):
                    with cols[i % 3]:
                        card(
                            title=path['role'],
                            text=f"{path['demand']} Demand | {path['avg_salary']}",
                            styles={"card": {"background-color": "#1E1E26", "color": "white"}}
                        )
                
                # --- Roadmap Tabs ---
                tab1, tab2 = st.tabs(["📚 Roadmap", "🏗️ Projects"])
                with tab1:
                    st.subheader("Your Learning Journey")
                    st.write("*Phase 1 (Short Term):*")
                    for item in data['Learning Roadmap']['Short Term']: st.write(f"🔹 {item}")
                    st.write("*Phase 2 (Long Term):*")
                    for item in data['Learning Roadmap']['Long Term']: st.write(f"🚀 {item}")
                
                with tab2:
                    st.subheader("Hands-on Projects")
                    st.info(f"*Try these first:* {', '.join(data['Projects']['Beginner'])}")
                    st.success(f"*Final Boss Level:* {', '.join(data['Projects']['Advanced'])}")

                st.divider()
                st.write(f"✨ *Inspiration:* {data.get('Motivation')}")

            except Exception as e:
                st.error("Model version 2.5 might not be active or JSON was malformed. Try using 1.5 if this persists.")
    else:
        st.warning("Please fill in all details!")
