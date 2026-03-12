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

def load_lottie(url):
    try:
        return requests.get(url).json()
    except:
        return None

# --- 4. THE AI LOGIC (Fixed Line 58 Logic) ---
def get_guidance(edu, skl, its, gol):
    # Using 'gemini-1.5-flash' for maximum stability
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We use a clean f-string here to avoid 'decimal literal' issues
    user_context = f"Education: {edu}, Skills: {skl}, Interests: {its}, Goals: {gol}"
    
    prompt = f"""
    Analyze this profile: {user_context}
    Provide a career roadmap in English.
    Return ONLY a JSON object.
    Format:
    {{
      "Paths": [
        {{"role": "Job Title", "demand": "High", "salary": "Range", "why": "Explanation"}}
      ],
      "Skills": [
        {{"name": "Skill Name", "type": "Technical"}}
      ],
      "Roadmap": {{
        "Short": ["Step 1"],
        "Long": ["Step 2"]
      }},
      "Projects": {{
        "Beginner": ["Project A"],
        "Advanced": ["Project B"]
      }},
      "Motivation": "One quote"
    }}
    """
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Robust extraction using Regex
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except:
        return {"error": "AI response was not in proper JSON format. Please try again."}

# --- 5. APP UI ---
add_bg()
lottie_data = load_lottie("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_data:
    st_lottie(lottie_data, height=180)

st.title("🧭 Career Compass AI")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        u_edu = st.text_input("🎓 Your Education")
        u_skl = st.text_input("💻 Your Skills")
    with c2:
        u_its = st.text_input("🎨 Your Interests")
        u_gol = st.text_input("🎯 Your Goals")

if st.button("🚀 Generate Roadmap", use_container_width=True):
    if u_edu and u_skl and u_its and u_gol:
        with st.spinner("Generating..."):
            res = get_guidance(u_edu, u_skl, u_its, u_gol)
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.balloons()
                
                # Career Path Cards
                st.subheader("🎯 Career Paths")
                paths = res.get("Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                for i, p in enumerate(paths):
                    with cols[i % 3]:
                        card(title=p['role'], text=f"{p['demand']} Demand | {p['salary']}", 
                             styles={"card": {"background-color": "#1E1E26", "color": "white"}})
                        with st.expander("Why?"): st.write(p['why'])

                # Roadmap Tabs
                t1, t2 = st.tabs(["🗺️ Roadmap", "🏗️ Projects"])
                with t1:
                    st.write("*Short Term:*")
                    for s in res['Roadmap']['Short']: st.write(f"✅ {s}")
                    st.write("*Long Term:*")
                    for s in res['Roadmap']['Long']: st.write(f"🚀 {s}")
                with t2:
                    st.info(f"*Beginner:* {', '.join(res['Projects']['Beginner'])}")
                    st.success(f"*Advanced:* {', '.join(res['Projects']['Advanced'])}")
                
                st.divider()
                st.info(f"✨ {res.get('Motivation')}")
    else:
        st.warning("Please fill all fields.")
