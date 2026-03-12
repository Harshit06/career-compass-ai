import streamlit as st
import google.generativeai as genai
import json
import requests
import time
from streamlit_lottie import st_lottie
from streamlit_card import card

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide"
)

# --- 2. API CONFIGURATION (Streamlit Secrets) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🚨 API Key nahi mili! Streamlit Secrets mein 'GOOGLE_API_KEY' set karein.")
    st.stop()

# --- 3. UI STYLING & ANIMATIONS ---
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
        .stTextInput>div>div>input {
            background-color: #1E1E26;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# --- 4. CORE AI LOGIC (Gemini 2.5 Flash) ---
def get_gemini_response(education, skills, interests, goals):
    # Model 2.5 Flash as requested
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a professional Career Advisor. Based on the following details:
    Education: {education}
    Skills: {skills}
    Interests: {interests}
    Goals: {goals}

    Generate a complete career guidance package. 
    Return ONLY a valid JSON object. Do not use backticks or markdown formatting.
    Structure:
    {{
      "Career Paths": [
        {{"role": "Job Title", "demand": "High/Med", "avg_salary": "Range", "reason": "Why this fits"}}
      ],
      "Skills to Learn": [
        {{"name": "Skill", "type": "Technical/Soft", "resources": ["Resource Name"]}}
      ],
      "Learning Roadmap": {{
        "Short Term": ["Step 1", "Step 2"],
        "Long Term": ["Step 3", "Step 4"]
      }},
      "Projects": {{
        "Beginner": ["Project A"],
        "Advanced": ["Project B"]
      }},
      "Opportunities": [
        {{"platform": "Website", "role": "Position", "skill_gap": "What to learn"}}
      ],
      "Motivation": "Inspirational Quote"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean JSON if model returns markdown
        if "json" in text:
            text = text.split("json")[1].split("")[0].strip()
        elif "" in text:
            text = text.split("")[1].split("")[0].strip()
            
        return json.loads(text)
    except Exception as e:
        return {"error": f"AI Error: {str(e)}"}

# --- 5. MAIN APP INTERFACE ---
add_animated_background()

# Animation Header
lottie_anim = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_anim:
    st_lottie(lottie_anim, height=200, key="header")

st.title("🧭 Career Compass AI")
st.markdown("### Build your future with Gemini 2.5 Intelligence")

# Input Section
with st.container():
    st.markdown("#### Apni Details Bhariye:")
    col1, col2 = st.columns(2)
    with col1:
        edu = st.text_input("🎓 Education", placeholder="e.g. B.Tech CS, BCA, MBA")
        skl = st.text_input("💻 Current Skills", placeholder="e.g. Python, Excel, Marketing")
    with col2:
        its = st.text_input("🎨 Interests", placeholder="e.g. Data Science, Gaming, Writing")
        gol = st.text_input("🎯 Career Goals", placeholder="e.g. Remote Job in MNC")

# Execution
if st.button("🚀 Generate My Career Path", use_container_width=True):
    if all([edu, skl, its, gol]):
        with st.spinner("AI aapke liye best options dhund raha hai..."):
            data = get_gemini_response(edu, skl, its, gol)
            
            if "error" in data:
                st.error(data["error"])
            else:
                st.balloons()
                
                # --- Career Path Cards ---
                st.subheader("🎯 Recommended Career Paths")
                paths = data.get("Career Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                for idx, path in enumerate(paths):
                    with cols[idx % 3]:
                        card(
                            title=path['role'],
                            text=f"Demand: {path['demand']} | Salary: {path['avg_salary']}",
                            styles={"card": {"background-color": "#262730", "color": "#FAFAFA", "border-radius": "15px"}}
                        )
                        with st.expander("Kyu ye path?"):
                            st.write(path['reason'])

                # --- Detailed Roadmap Tabs ---
                st.divider()
                tab1, tab2, tab3 = st.tabs(["🗺️ Roadmap", "🏗️ Projects", "💼 Jobs"])
                
                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### 🛠️ Skills to Acquire")
                        for s in data.get("Skills to Learn", []):
                            st.write(f"✅ *{s['name']}* ({s['type']})")
                    with c2:
                        st.markdown("### 🗺️ Timeline")
                        st.write("*Next 6 Months:*")
                        for step in data['Learning Roadmap']['Short Term']: st.write(f"🔹 {step}")
                        st.write("*Next 2 Years:*")
                        for step in data['Learning Roadmap']['Long Term']: st.write(f"🚀 {step}")

                with tab2:
                    st.markdown("### 🚀 Portfolio Builders")
                    st.info(f"*Beginner:* {', '.join(data['Projects']['Beginner'])}")
                    st.success(f"*Advanced:* {', '.join(data['Projects']['Advanced'])}")

                with tab3:
                    st.markdown("### 🌍 Job Opportunities")
                    for opp in data.get("Opportunities", []):
                        st.write(f"📍 *{opp['role']}* on {opp['platform']}")
                        st.caption(f"Gap to fill: {opp['skill_gap']}")

                st.divider()
                st.info(f"✨ *Motivation:* {data.get('Motivation')}")
    else:
        st.warning("Saari details bharna zaroori hai!")
