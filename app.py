import streamlit as st

st.set_page_config(page_title="WASL - وَصل", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #12082d;
        color: white;
        font-family: 'Times New Roman', Times, serif;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 1.5rem;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
    }

    .header-frame {
        border: 1px solid #4a4a8a;
        border-radius: 8px;
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .header-spacer { flex: 1; }
    .room-no-pill {
        background-color: #413c52;
        border: 1px solid #8a8ab0;
        border-radius: 4px;
        padding: 6px 18px;
    }
    .wasl-logo {
        flex: 1;
        text-align: right;
        color: #508782;
        line-height: 1.3;
    }

    .box {
        background-color: #12082d;
        border: 1px solid white;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .box-notes {
        background-color: #676279;
        border-radius: 10px;
