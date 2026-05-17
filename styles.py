import streamlit as st
 
def apply_custom_css():
    st.markdown("""
    <style>
 
    .date-text {
        color: #666;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: -10px;
    }

    .greeting-container {
        display: flex;
        align-items: baseline;
        gap: 10px;
        margin-bottom: 0;
    }
    .greeting-text {
        color: white;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
    .name-text {
        color: #4CAF50;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
 
    .greeting-container + div[data-testid="stButton"] {
        margin-top: -3.2rem;
        margin-left: 420px;
        width: fit-content;
    }
 
    .greeting-container + div[data-testid="stButton"] button {
        background: transparent;
        border: none;
        color: #666;
        font-size: 1.2rem;
        padding: 0 0.3rem;
        cursor: pointer;
        line-height: 1;
    }
    .greeting-container + div[data-testid="stButton"] button:hover {
        color: #4CAF50;
        background: transparent;
        border: none;
    }
 
    div[data-testid="stTextInput"] label {
        display: none;
    }
 
    </style>
    """, unsafe_allow_html=True)
 