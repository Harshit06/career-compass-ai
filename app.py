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
    css = """
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
