import streamlit as st

st.set_page_config(page_title="WASL - وَصل", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #12082d;
        color: white;
        font-family: 'Times New Roman', Times, serif;
    }
    .header-frame {
        border: 1px solid #4a4a8a;
        border-radius: 8px;
        padding: 14px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'Times New Roman', Times, serif;
        margin-bottom: 16px;
    }
    .header-spacer { flex: 1; }
    .room-no-pill {
        background-color: #413c52;
        border: 1px solid #8a8ab0;
        border-radius: 4px;
        padding: 6px 18px;
        text-align: center;
    }
    .wasl-logo {
        flex: 1;
        text-align: right;
        color: #508782;
    }
    .box {
        background-color: #12082d;
        border: 1px solid white;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Times New Roman', Times, serif;
    }
    .box-notes {
        background-color: #676279;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Times New Roman', Times, serif;
        min-height: 36vh;
    }
    .box-notes hr { border-color: white; }
    .teal-pill {
        background-color: #508782;
        border-radius: 20px;
        padding: 6px 24px;
        display: inline-block;
    }
    .top-left-box { min-height: 55vh; }
    .bottom-right-box { min-height: 30vh; }
    </style>
""", unsafe_allow_html=True)

# ===== الشريط العلوي (إطار واحد متصل) =====
st.markdown("""
    <div class='header-frame'>
        <div class='header-spacer'></div>
        <div class='room-no-pill'>Room no</div>
        <div class='wasl-logo'><b style='font-size:20px;'>WASL</b><br>وَصل</div>
    </div>
""", unsafe_allow_html=True)

# ===== الأعمدة بنسب مطابقة للتصميم (36% / 56%) =====
left_col, right_col = st.columns([36, 56])

with left_col:
    st.markdown("""
        <div class='box top-left-box'>
            <div style='text-align:right;'><span class='teal-pill'>&nbsp;&nbsp;&nbsp;&nbsp;</span></div>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
        <div class='box-notes'>
            <b>Patient Notes:</b><hr>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)")
    st.write("")
    st.markdown("<div class='box bottom-right-box'></div>", unsafe_allow_html=True)
