import streamlit as st
import google.generativeai as genai
import json
import requests
import re
from streamlit_lottie import st_lottie
from streamlit_card import card

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Career Compass AI", page_icon="🧭", layout="wide")

# --- 2. API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🚨 API Key missing! Add 'GOOGLE_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 3. UI HELPERS ---
def add_bg():
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

# --- 4. THE AI LOGIC (With Model Fallback) ---
def get_guidance(edu, skl, its, gol):
    # List of models to try in order of preference
    # 'gemini-2.0-flash' or 'gemini-1.5-flash-8b' are often more available
    model_options = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
    
    prompt = f"""
    Act as a Career Mentor. Provide a roadmap in English for:
    Education: {edu}, Skills: {skl}, Interests: {its}, Goals: {gol}.
    Return ONLY JSON:
    {{
      "Paths": [{{ "role": "Title", "demand": "High", "salary": "Range", "why": "Text" }}],
      "Skills": [{{ "name": "Skill", "type": "Tech" }}],
      "Roadmap": {{ "Short": ["Step1"], "Long": ["Step2"] }},
      "Projects": {{ "Beginner": ["P1"], "Advanced": ["P2"] }},
      "Motivation": "Quote"
    }}
    """

    success = False
    res_data = None
    error_msg = ""

    for model_name in model_options:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if response and response.text:
                text = response.text.strip()
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    res_data = json.loads(match.group())
                    success = True
                    break
        except Exception as e:
            error_msg = str(e)
            continue # Try next model if this one fails

    if success:
        return res_data
    else:
        return {"error": f"All models failed. Last error: {error_msg}"}

# --- 5. APP UI ---
add_bg()
st.title("🧭 Career Compass AI")
st.write("Your AI-Powered Career Roadmap")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        u_edu = st.text_input("🎓 Education", placeholder="e.g. Law Student")
        u_skl = st.text_input("💻 Skills", placeholder="e.g. Research, Public Speaking")
    with c2:
        u_its = st.text_input("🎨 Interests", placeholder="e.g. Tech Law, Robotics")
        u_gol = st.text_input("🎯 Goals", placeholder="e.g. Legal Consultant for Tech Firms")

if st.button("🚀 Generate Roadmap", use_container_width=True):
    if u_edu and u_skl and u_its and u_gol:
        with st.spinner("Finding the best AI model for you..."):
            res = get_guidance(u_edu, u_skl, u_its, u_gol)
            
            if "error" in res:
                st.error(res["error"])
                st.info("Check if 'Generative Language API' is enabled in your Google Cloud Project.")
            else:
                st.balloons()
                
                # Career Path Cards
                st.subheader("🎯 Career Paths")
                paths = res.get("Paths", [])
                if paths:
                    cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                    for i, p in enumerate(paths):
                        with cols[i % 3]:
                            card(title=p['role'], text=f"{p['demand']} Demand | {p['salary']}", 
                                 styles={"card": {"background-color": "#1E1E26", "color": "white"}})
                            with st.expander("Why?"): st.write(p['why'])

                # Roadmap Tabs
                t1, t2 = st.tabs(["🗺️ Roadmap", "🏗️ Projects"])
                with t1:
                    st.write("*Phase 1:*")
                    for s in res.get('Roadmap', {}).get('Short', []): st.write(f"✅ {s}")
                    st.write("*Phase 2:*")
                    for s in res.get('Roadmap', {}).get('Long', []): st.write(f"🚀 {s}")
                with t2:
                    st.info(f"*Beginner:* {', '.join(res.get('Projects', {}).get('Beginner', []))}")
                    st.success(f"*Advanced:* {', '.join(res.get('Projects', {}).get('Advanced', []))}")
                
                st.divider()
                st.info(f"✨ {res.get('Motivation')}")
    else:
        st.warning("Please fill all fields.")
