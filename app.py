[9:16 PM, 3/12/2026] Harshit Voda: import streamlit as st
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
       …
[9:18 PM, 3/12/2026] Harshit Voda: import streamlit as st
import google.generativeai as genai
import json
import requests
import re
from streamlit_lottie import st_lottie
from streamlit_card import card

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Career Compass AI", 
    page_icon="🧭", 
    layout="wide"
)

# --- 2. API SETUP ---
# Ensure GOOGLE_API_KEY is in your Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("🚨 API Key not found! Add 'GOOGLE_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 3. UI HELPERS ---
def add_custom_css():
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

def load_lottie_url(url):
    try:
        return requests.get(url).json()
    except:
        return None

# --- 4. ROBUST AI LOGIC ---
def get_career_guidance(edu, skl, its, gol):
    # Using Gemini 2.5 Flash as requested
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Analyze the following user profile and provide a career roadmap:
    - Education: {edu}
    - Current Skills: {skl}
    - Interests: {its}
    - Goals: {gol}

    Return ONLY a valid JSON object. Do not include markdown formatting or extra text.
    Required Structure:
    {{
      "Paths": [
        {{"role": "Title", "demand": "High/Med", "salary": "Range", "why": "Explanation"}}
      ],
      "Skills": [
        {{"name": "Skill Name", "type": "Technical/Soft"}}
      ],
      "Roadmap": {{
        "ShortTerm": ["Step 1", "Step 2"],
        "LongTerm": ["Step 3", "Step 4"]
      }},
      "Projects": {{
        "Beginner": ["Project 1"],
        "Advanced": ["Project 2"]
      }},
      "Motivation": "One inspirational sentence"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # FIX: Robust JSON extraction using Regex to avoid "empty separator" errors
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw_text)
    except Exception as e:
        return {"error": f"Failed to process AI response: {str(e)}"}

# --- 5. MAIN APP INTERFACE ---
add_custom_css()

# Header Animation
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json"
lottie_data = load_lottie_url(lottie_url)
if lottie_data:
    st_lottie(lottie_data, height=180, key="header_anim")

st.title("🧭 Career Compass AI")
st.markdown("Your Personalized AI Mentor for Professional Growth")

# User Input Form
with st.container():
    st.subheader("Profile Details")
    col1, col2 = st.columns(2)
    with col1:
        edu_input = st.text_input("🎓 Education", placeholder="e.g., B.S. in Computer Science")
        skl_input = st.text_input("💻 Current Skills", placeholder="e.g., Python, Data Analysis, SQL")
    with col2:
        its_input = st.text_input("🎨 Interests", placeholder="e.g., Artificial Intelligence, UI Design")
        gol_input = st.text_input("🎯 Career Goals", placeholder="e.g., Become a Senior Software Engineer")

# Submission Logic
if st.button("🚀 Generate My Roadmap", use_container_width=True):
    if edu_input and skl_input and its_input and gol_input:
        with st.spinner("Analyzing market trends and crafting your path..."):
            result = get_career_guidance(edu_input, skl_input, its_input, gol_input)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.balloons()
                st.success("Your roadmap is ready!")

                # --- Recommended Paths ---
                st.header("🎯 Recommended Career Paths")
                paths = result.get("Paths", [])
                cols = st.columns(len(paths) if 0 < len(paths) <= 3 else 3)
                
                for i, path in enumerate(paths):
                    with cols[i % 3]:
                        card(
                            title=path['role'],
                            text=f"🔥 Demand: {path['demand']} | 💰 {path['salary']}",
                            styles={"card": {"background-color": "#1E1E26", "color": "white", "border-radius": "12px"}}
                        )
                        with st.expander("Why this fits?"):
                            st.write(path['why'])

                # --- Detailed Strategy ---
                st.divider()
                tab1, tab2 = st.tabs(["🗺️ Skills & Timeline", "🏗️ Project Ideas"])
                
                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### 🛠️ Skills to Learn")
                        for s in result.get("Skills", []):
                            st.write(f"✅ *{s['name']}* ({s['type']})")
                    with c2:
                        st.markdown("### 🗺️ Timeline")
                        st.markdown("*Next 6 Months:*")
                        for step in result['Roadmap'].get('ShortTerm', []): st.write(f"🔹 {step}")
                        st.markdown("*Longer Term:*")
                        for step in result['Roadmap'].get('LongTerm', []): st.write(f"🚀 {step}")

                with tab2:
                    st.markdown("### 🚀 Portfolio Builders")
                    st.info(f"*Beginner Projects:* {', '.join(result['Projects']['Beginner'])}")
                    st.success(f"*Advanced Challenges:* {', '.join(result['Projects']['Advanced'])}")

                st.divider()
                st.info(f"✨ *Motivation:* {result.get('Motivation')}")
    else:
        st.warning("Please fill out all fields to generate your roadmap."
