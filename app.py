import streamlit as st
import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from streamlit_card import card
import requests

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide"
)

# --- Custom CSS for a "Cool & Animated" UI ---
def load_css():
    # Using a raw string (r"..."") to prevent character escaping issues
    css = r"""
    <style>
    /* Import a professional font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Poppins', sans-serif;
    }

    /* --- Animation --- */
    /* Gentle fade-in animation for elements */
    @keyframes fadeIn {
      from { 
        opacity: 0; 
        transform: translateY(20px); 
      }
      to { 
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* Apply animation to the form and the result cards */
    [data-testid="stForm"], div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        animation: fadeIn 0.8s ease-out;
    }

    /* --- Styling --- */
    .stApp {
        background-color: #0E1117;
    }
    [data-testid="stForm"] {
        border: 1px solid #262730;
        border-radius: 15px;
        padding: 25px;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"]:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 30px rgba(160, 122, 255, 0.3);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Helper Functions ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

def animated_title(text):
    title_placeholder = st.empty()
    typed_text = ""
    for char in text:
        typed_text += char
        title_placeholder.title(typed_text + "▌")
        time.sleep(0.05)
    title_placeholder.title(text)

def display_skills(skill_list, skill_type):
    st.markdown(f"**{skill_type} Skills**")
    badges = "".join([f'<span style="display: inline-block; background-color: #262730; color: #FAFAFA; padding: 5px 12px; margin: 3px; border-radius: 15px; border: 1px solid #A07AFF;">{skill["name"]}</span>' for skill in skill_list])
    st.markdown(badges, unsafe_allow_html=True)

def get_gemini_response(education, skills, interests, goals):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    You are an AI-powered Personalized Career and Skills Advisor. Analyze the user's profile: Education:{education}, Skills:{skills}, Interests:{interests}, Goals:{goals}. Generate a complete career guidance package in a structured JSON format ONLY.
    The JSON structure must be: {{"Career Paths":[{{"role":"string","demand":"string","avg_salary":"string","reason":"string"}}], "Skills to Learn":[{{"name":"string","type":"string"}}], "Learning Roadmap":{{"Short Term":["string"],"Long Term":["string"]}}, "Projects":{{"Beginner":["string"],"Advanced":["string"]}}, "Opportunities":[{{"platform":"string","role":"string","skill_gap":"string"}}], "Motivation":"string"}}
    """
    response = model.generate_content(prompt)
    return response.text

# --- Load API Key ---
load_dotenv()
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found. Please add it to your .env file.", icon="🚨")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring API: {e}", icon="🚨")

# --- Main App UI ---
load_css() # Load the custom CSS

lottie_json = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_json:
    st_lottie(lottie_json, speed=1, height=200, key="initial_animation")

animated_title("🧭 Career Compass AI") # The animated typing title
st.write("Your Personal AI Mentor for a Successful Career Path")

with st.form("user_profile_form"):
    st.subheader("Tell Us About Yourself")
    
    c1, c2 = st.columns(2)
    with c1:
        education = st.text_input("🎓 Your Education", placeholder="e.g., B.Tech in Computer Science, 3rd Year")
        skills = st.text_input("💻 Your Current Skills", placeholder="e.g., Python, Java, Basic Data Structures")
    with c2:
        interests = st.text_input("🎨 Your Interests", placeholder="e.g., AI, Gaming, Problem Solving")
        goals = st.text_input("🎯 Your Career Goals", placeholder="e.g., Get a high-paying job at a FAANG company")

    submit_button = st.form_submit_button(label="🚀 Generate My Career Path")

# --- Output Section ---
if submit_button:
    if all([education, skills, interests, goals]):
        with st.spinner("Crafting your future... Please wait!"):
            try:
                response_text = get_gemini_response(education, skills, interests, goals)
                response_data = json.loads(response_text.strip("```json\n"))
                st.balloons()
                
                st.success("Your Personalized Career Roadmap is Ready!")
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.subheader("🎯 Recommended Career Paths")
                paths = response_data.get("Career Paths", [])
                if paths:
                    cols = st.columns(len(paths))
                    for i, path in enumerate(paths):
                        with cols[i]:
                            card(title=path['role'],
                                 text=[f"Demand: {path['demand']}", f"Salary: {path['avg_salary']}", path['reason']],
                                 styles={"card": {"background-color": "#262730", "color": "#FAFAFA"}})
                
                st.divider()
                
                tab1, tab2, tab3 = st.tabs(["🗺️ Skills to Learn", "🗓️ Learning Roadmap", "🚀 Projects & Opportunities"])

                with tab1:
                    st.header("Skills to Learn")
                    tech_skills = [s for s in response_data.get("Skills to Learn", []) if s['type'] == 'Technical']
                    soft_skills = [s for s in response_data.get("Skills to Learn", []) if s['type'] != 'Technical']
                    
                    display_skills(tech_skills, "Technical")
                    st.markdown("<br>", unsafe_allow_html=True)
                    display_skills(soft_skills, "Soft")

                with tab2:
                    st.header("Your Learning Roadmap")
                    roadmap = response_data.get("Learning Roadmap", {})
                    with st.container(border=True):
                        st.markdown("**Short-Term (Next 3-6 Months):**")
                        for item in roadmap.get("Short Term", []): st.checkbox(item, key=f"st_{item}")
                    with st.container(border=True):
                        st.markdown("**Long-Term (6 Months - 2 Years):**")
                        for item in roadmap.get("Long Term", []): st.checkbox(item, key=f"lt_{item}")
                
                with tab3:
                    st.header("Projects to Build Your Portfolio")
                    projects = response_data.get("Projects", {})
                    with st.expander("**Beginner Projects**"):
                        for proj in projects.get("Beginner", []): st.markdown(f"- {proj}")
                    with st.expander("**Advanced Project**"):
                        st.markdown(f"- {projects.get('Advanced', [''])[0]}")
                    
                    st.divider()
                    st.header("Job & Internship Opportunities")
                    for opp in response_data.get("Opportunities", []):
                        st.info(f"**Role:** {opp['role']} on **{opp['platform']}**\n\n**Skill Gap to Fill:** {opp['skill_gap']}")

                st.divider()
                st.success(f"**⭐ Motivational Boost:** {response_data.get('Motivation')}")

            except Exception as e:
                st.error(f"An error occurred: {e}", icon="🔥")
    else:
        st.warning("Please fill out all the fields.")
