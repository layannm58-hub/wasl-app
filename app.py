import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="WASL - وَصل",
    layout="wide"
)

# الألوان والخط المطابقين للتصميم الأصلي
st.markdown("""
    <style>
    .stApp {
        background-color: #12082d;
        color: white;
        font-family: 'Times New Roman', Times, serif;
    }
    .box {
        background-color: #12082d;
        border: 1px solid white;
        border-radius: 4px;
        padding: 20px;
        min-height: 200px;
        font-family: 'Times New Roman', Times, serif;
    }
    .box-light {
        background-color: #e7e7e7;
        color: black;
        border-radius: 4px;
        padding: 20px;
        min-height: 200px;
    }
    .box-notes {
        background-color: #676279;
        border: 1px solid #999;
        border-radius: 4px;
        padding: 20px;
        min-height: 200px;
        font-family: 'Times New Roman', Times, serif;
    }
    .box-notes hr {
        border-color: white;
    }
    .header-bar {
        border: 1px solid #4a4a7a;
        border-radius: 4px;
        padding: 12px;
        font-family: 'Times New Roman', Times, serif;
    }
    .teal-pill {
        background-color: #508782;
        border-radius: 20px;
        padding: 6px 20px;
        display: inline-block;
        color: white;
    }
    .wasl-logo {
        text-align: right;
        color: #508782;
        font-family: 'Times New Roman', Times, serif;
    }
    </style>
""", unsafe_allow_html=True)

# ===== الشريط العلوي =====
header_col1, header_col2, header_col3 = st.columns([1, 1, 1])
with header_col2:
    st.markdown("<div class='header-bar' style='text-align:center;'>Room no</div>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<div class='wasl-logo'><b style='font-size:22px;'>WASL</b><br>وَصل</div>", unsafe_allow_html=True)

st.write("")  # مسافة فاصلة

# ===== الأعمدة الرئيسية (يسار ويمين) =====
left_col, right_col = st.columns(2)

# --- العمود الأيسر ---
with left_col:
    st.markdown("""
        <div class='box'>
            <div style='text-align:right;'>
                <span class='teal-pill'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
        <div class='box-notes'>
            <b>Patient Notes:</b>
            <hr>
        </div>
    """, unsafe_allow_html=True)

# --- العمود الأيمن ---
with right_col:
    # مكان الكاميرا (Placeholder حاليًا)
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)")
    st.write("")
    st.markdown("<div class='box'></div>", unsafe_allow_html=True)
