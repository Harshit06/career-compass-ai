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

# --- 4. AUTO-DISCOVERY AI LOGIC ---
def get_guidance(edu, skl, its, gol):
    # STEP 1: Find any available model that supports generation
    available_model = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_model = m.name
                break
    except Exception as e:
        return {"error": f"Could not list models: {str(e)}"}

    if not available_model:
        return {"error": "No compatible Gemini models found on this API key."}

    # STEP 2: Use the discovered model
    try:
        model = genai.GenerativeModel(available_model)
        prompt = f"""
        Act as a Career Mentor. Provide a roadmap in English for:
        Education: {edu}, Skills: {skl}, Interests: {its}, Goals: {gol}.
        Return ONLY a JSON object:
        {{
          "Paths": [{{ "role": "Title", "demand": "High", "salary": "Range", "why": "Text" }}],
          "Skills": [{{ "name": "Skill", "type": "Tech" }}],
          "Roadmap": {{ "Short": ["Step1"], "Long": ["Step2"] }},
          "Projects": {{ "Beginner": ["P1"], "Advanced": ["P2"] }},
          "Motivation": "Quote"
        }}
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception as e:
        return {"error": f"Model {available_model} failed: {str(e)}"}

# --- 5. APP UI ---
add_bg()
st.title("🧭 Career Compass AI")
st.write("Using automated model discovery to find the best path for you.")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        u_edu = st.text_input("🎓 Education", placeholder="e.g. Law Student at Central Law College")
        u_skl = st.text_input("💻 Skills", placeholder="e.g. Legal Research, English")
    with c2:
        u_its = st.text_input("🎨 Interests", placeholder="e.g. Robotics, Coding")
        u_gol = st.text_input("🎯 Goals", placeholder="e.g. Tech-Legal Consultant")

if st.button("🚀 Generate Roadmap", use_container_width=True):
    if u_edu and u_skl and u_its and u_gol:
        with st.spinner("Searching for available AI models..."):
            res = get_guidance(u_edu, u_skl, u_its, u_gol)
            
            if "error" in res:
                st.error(res["error"])
                st.info("Ensure the 'Generative Language API' is enabled in your Google Cloud Console.")
            else:
                st.balloons()
                
                # Career Path Cards
                st.subheader("🎯 Career Paths")
                paths = res.get("Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                for i, p in enumerate(paths):
                    with cols[i % 3]:
                        card(title=p['role'], text=f"{p['demand']} Demand", 
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
