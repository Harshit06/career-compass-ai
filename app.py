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
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key! Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. Custom CSS for Animation
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
        .main-card {
            background-color: rgba(38, 39, 48, 0.7);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #4B3978;
        }
        </style>
    """, unsafe_allow_html=True)

# 4. Helper Functions
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_gemini_response(education, skills, interests, goals):
    # Using the current stable 1.5 Flash model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a Career Mentor. Analyze this profile:
    - Education: {education}
    - Current Skills: {skills}
    - Interests: {interests}
    - Career Goals: {goals}

    Return ONLY a valid JSON object. Do not include markdown formatting or backticks.
    {{
      "Career Paths": [
        {{"role": "Title", "demand": "High/Medium", "avg_salary": "Range", "reason": "Why"}}
      ],
      "Skills to Learn": [
        {{"name": "Skill Name", "type": "Technical/Soft", "resources": ["Link/Source"]}}
      ],
      "Learning Roadmap": {{
        "Short Term": ["Step 1", "Step 2"],
        "Long Term": ["Step 1", "Step 2"]
      }},
      "Projects": {{
        "Beginner": ["Project 1"],
        "Advanced": ["Project 2"]
      }},
      "Opportunities": [
        {{"platform": "Name", "role": "Type", "skill_gap": "What to learn"}}
      ],
      "Motivation": "Inspirational Quote"
    }}
    """
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Robust JSON Cleaning
    if text.startswith("json"):
        text = text.split("json")[1].split("")[0].strip()
    elif text.startswith(""):
        text = text.split("")[1].split("")[0].strip()
        
    return text

# --- App Execution ---
add_animated_background()

# Header Section
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json"
lottie_json = load_lottieurl(lottie_url)
if lottie_json:
    st_lottie(lottie_json, height=200, key="header_anim")

st.title("🧭 Career Compass AI")
st.markdown("---")

# Input Form
with st.container():
    st.subheader("Your Profile Details")
    col1, col2 = st.columns(2)
    with col1:
        education = st.text_input("🎓 Education", placeholder="e.g. B.Tech CS, Final Year")
        skills = st.text_input("💻 Current Skills", placeholder="e.g. Python, SQL, Git")
    with col2:
        interests = st.text_input("🎨 Interests", placeholder="e.g. Machine Learning, Finance")
        goals = st.text_input("🎯 Career Goals", placeholder="e.g. Data Scientist at a Top Firm")

# Action Button
if st.button("🚀 Generate My Career Roadmap", use_container_width=True):
    if all([education, skills, interests, goals]):
        with st.spinner("Our AI is navigating the best paths for you..."):
            try:
                response_json = get_gemini_response(education, skills, interests, goals)
                data = json.loads(response_json)
                
                st.balloons()
                st.success("Your personalized roadmap is ready!")

                # --- Section 1: Career Paths ---
                st.header("🎯 Recommended Careers")
                paths = data.get("Career Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                
                for idx, path in enumerate(paths):
                    with cols[idx % 3]:
                        card(
                            title=path['role'],
                            text=f"🔥 Demand: {path['demand']} | 💰 {path['avg_salary']}",
                            styles={"card": {"background-color": "#1E1E26", "color": "white", "border-radius": "10px"}}
                        )
                        with st.expander("Detailed Insight"):
                            st.write(path['reason'])

                # --- Section 2: Skills & Roadmap ---
                st.divider()
                tab1, tab2, tab3 = st.tabs(["📚 Learning Plan", "🏗️ Projects", "💼 Opportunities"])

                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### 🛠️ Skills to Acquire")
                        for s in data.get("Skills to Learn", []):
                            st.write(f"*{s['name']}* - {s['type']}")
                    with c2:
                        st.markdown("### 🗺️ Timeline")
                        st.markdown("*Next 6 Months:*")
                        for step in data['Learning Roadmap']['Short Term']: st.write(f"✅ {step}")
                        st.markdown("*Longer Horizon:*")
                        for step in data['Learning Roadmap']['Long Term']: st.write(f"🚀 {step}")

                with tab2:
                    st.markdown("### 🚀 Portfolio Builders")
                    st.info(f"*Beginner Projects:* {', '.join(data['Projects']['Beginner'])}")
                    st.success(f"*Advanced Projects:* {', '.join(data['Projects']['Advanced'])}")

                with tab3:
                    st.markdown("### 🌍 Job Market & Platforms")
                    for opp in data.get("Opportunities", []):
                        st.write(f"📍 *{opp['role']}* on *{opp['platform']}*")
                        st.caption(f"Bridge the gap: {opp['skill_gap']}")

                st.divider()
                st.info(f"💡 *Motivational Boost:* {data.get('Motivation')}")

            except Exception as e:
                st.error("Error generating roadmap. Please try again or refine your inputs.")
                # st.exception(e) # Uncomment for debugging
    else:
        st.warning("Please fill out all the fields above!")
