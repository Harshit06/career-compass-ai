import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from streamlit_card import card
import requests

# Page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide"
)

# Load environment variables and configure the API
load_dotenv()
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found. Please add it to your .env file.", icon="🚨")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring API: {e}", icon="🚨")

# Helper functions
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def get_gemini_response(education, skills, interests, goals):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    You are an AI-powered Personalized Career and Skills Advisor. Analyze the user's profile: Education:{education}, Skills:{skills}, Interests:{interests}, Goals:{goals}. Generate a complete career guidance package in a structured JSON format ONLY.
    The JSON structure must be: {{"Career Paths":[{{"role":"string","demand":"string","avg_salary":"string","reason":"string"}}], "Skills to Learn":[{{"name":"string","type":"string","resources":["string","string"]}}], "Learning Roadmap":{{"Short Term":["string"],"Long Term":["string"]}}, "Projects":{{"Beginner":["string"],"Advanced":["string"]}}, "Opportunities":[{{"platform":"string","role":"string","skill_gap":"string"}}], "Motivation":"string"}}
    """
    response = model.generate_content(prompt)
    return response.text

# --- Main App UI ---
lottie_json = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_DMgKk1.json")
if lottie_json:
    st_lottie(lottie_json, speed=1, height=200, key="initial")

st.title("🧭 Career Compass AI")
st.write("Your Personal AI Mentor for a Successful Career Path")

with st.form("user_profile_form"):
    st.subheader("Tell Us About Yourself")
    
    col1, col2 = st.columns(2)
    with col1:
        education = st.text_input("🎓 Your Education", placeholder="e.g., B.Tech in Computer Science, 3rd Year")
        skills = st.text_input("💻 Your Current Skills", placeholder="e.g., Python, Java")
    with col2:
        interests = st.text_input("🎨 Your Interests", placeholder="e.g., AI, Gaming")
        goals = st.text_input("🎯 Your Career Goals", placeholder="e.g., Get a high-paying job")
    submit_button = st.form_submit_button(label="🚀 Generate My Career Path")

if submit_button:
    if all([education, skills, interests, goals]):
        with st.spinner("Crafting your future..."):
            try:
                response_text = get_gemini_response(education, skills, interests, goals)
                response_data = json.loads(response_text.strip("```json\n"))
                st.balloons()
                
                st.success("Your Personalized Career Roadmap is Ready!")

                st.header("🎯 Recommended Career Paths")
                paths = response_data.get("Career Paths", [])
                if paths:
                    cols = st.columns(len(paths))
                    for i, path in enumerate(paths):
                        with cols[i]:
                            card(title=path['role'], text=[f"Demand: {path['demand']}", f"Salary: {path['avg_salary']}", path['reason']], styles={"card": {"background-color": "#262730", "color": "#FAFAFA"}})
                
                st.divider()
                tab2, tab3 = st.tabs(["🗺️ Skills & Roadmap", "🚀 Projects & Opportunities"])
                with tab2:
                    st.header("Skills to Learn")
                    tech_skills = [s for s in response_data.get("Skills to Learn", []) if s['type'] == 'Technical']
                    soft_skills = [s for s in response_data.get("Skills to Learn", []) if s['type'] != 'Technical']
                    c1_skills, c2_skills = st.columns(2)
                    with c1_skills:
                        st.markdown("**Technical Skills**")
                        for skill in tech_skills: st.markdown(f"- **{skill['name']}**")
                    with c2_skills:
                        st.markdown("**Soft Skills**")
                        for skill in soft_skills: st.markdown(f"- **{skill['name']}**")
                    st.divider()
                    st.header("Your Learning Roadmap")
                    roadmap = response_data.get("Learning Roadmap", {})
                    st.markdown("**Short-Term (Next 3-6 Months):**")
                    for item in roadmap.get("Short Term", []): st.checkbox(item, key=f"st_{item}")
                    st.markdown("**Long-Term (6 Months - 2 Years):**")
                    for item in roadmap.get("Long Term", []): st.checkbox(item, key=f"lt_{item}")

                with tab3:
                    st.header("Projects to Build Your Portfolio")
                    projects = response_data.get("Projects", {})
                    st.markdown("**Beginner Projects:**")
                    for proj in projects.get("Beginner", []): st.markdown(f"- {proj}")
                    st.markdown("**Advanced Project:**")
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
