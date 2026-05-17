import streamlit as st


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
    }
    .greeting-text {
        color: white;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
    .name-text {
        color: #4CAF50; /* Das Grün aus dem Bild */
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
    /* Versteckt den Standard-Label vom Input */
    div[data-testid="stTextInput"] label {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
