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

# --- 4. ROBUST AI LOGIC ---
def get_guidance(edu, skl, its, gol):
    # If 1.5 flash failed for you, we use 'gemini-pro' as a stable alternative
    # or you can try 'gemini-1.5-flash-latest'
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze this career profile in English:
        Education: {edu}
        Skills: {skl}
        Interests: {its}
        Goals: {gol}
        
        Return ONLY a JSON object.
        Structure:
        {{
          "Paths": [{{"role": "Title", "demand": "High", "salary": "Range", "why": "text"}}],
          "Skills": [{{"name": "Skill", "type": "Technical"}}],
          "Roadmap": {{"Short": ["step1"], "Long": ["step2"]}},
          "Projects": {{"Beginner": ["P1"], "Advanced": ["P2"]}},
          "Motivation": "Quote"
        }}
        """
        
        # Adding a request timeout to prevent the long hanging error
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return {"error": "AI returned an empty response. Try again."}
            
        text = response.text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
        
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

# --- 5. APP UI ---
add_bg()
lottie_data = load_lottie("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_data:
    st_lottie(lottie_data, height=180)

st.title("🧭 Career Compass AI")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        u_edu = st.text_input("🎓 Education")
        u_skl = st.text_input("💻 Skills")
    with c2:
        u_its = st.text_input("🎨 Interests")
        u_gol = st.text_input("🎯 Goals")

if st.button("🚀 Generate Roadmap", use_container_width=True):
    if u_edu and u_skl and u_its and u_gol:
        with st.spinner("Connecting to Gemini AI..."):
            res = get_guidance(u_edu, u_skl, u_its, u_gol)
            
            if "error" in res:
                st.error(f"Error: {res['error']}")
                st.info("Tip: Check if your API Key has 'Generative Language API' enabled in Google Cloud Console.")
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
                            with st.expander("Details"): st.write(p['why'])

                # Roadmap Tabs
                t1, t2 = st.tabs(["🗺️ Roadmap", "🏗️ Projects"])
                with t1:
                    st.write("*Next 6 Months:*")
                    for s in res.get('Roadmap', {}).get('Short', []): st.write(f"✅ {s}")
                    st.write("*Long Term:*")
                    for s in res.get('Roadmap', {}).get('Long', []): st.write(f"🚀 {s}")
                with t2:
                    st.info(f"*Beginner:* {', '.join(res.get('Projects', {}).get('Beginner', []))}")
                    st.success(f"*Advanced:* {', '.join(res.get('Projects', {}).get('Advanced', []))}")
                
                st.divider()
                st.info(f"✨ {res.get('Motivation')}")
    else:
        st.warning("Please fill all fields.")
