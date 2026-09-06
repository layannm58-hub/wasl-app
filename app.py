import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="WASL - وَصل",
    layout="wide"
)

# تلوين الخلفية والعناصر بألوان قريبة من التصميم
st.markdown("""
    <style>
    .stApp {
        background-color: #14102b;
        color: white;
    }
    .box {
        border: 1px solid white;
        border-radius: 10px;
        padding: 20px;
        min-height: 200px;
    }
    .box-light {
        background-color: #e8e8e8;
        color: black;
        border-radius: 10px;
        padding: 20px;
        min-height: 200px;
    }
    .box-notes {
        background-color: #6b6480;
        border-radius: 10px;
        padding: 20px;
        min-height: 200px;
    }
    </style>
""", unsafe_allow_html=True)

# ===== الشريط العلوي =====
header_col1, header_col2, header_col3 = st.columns([1, 1, 1])
with header_col2:
    st.markdown("<div style='text-align:center; border:1px solid #4a4a7a; border-radius:8px; padding:8px;'>Room no</div>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<div style='text-align:right; color:#4fa89b;'><b>WASL</b><br>وَصل</div>", unsafe_allow_html=True)

st.write("")  # مسافة فاصلة

# ===== الأعمدة الرئيسية (يسار ويمين) =====
left_col, right_col = st.columns(2)

# --- العمود الأيسر ---
with left_col:
    st.markdown("<div class='box'>معلومات المريض (لاحقًا)</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='box-notes'><b>Patient Notes:</b></div>", unsafe_allow_html=True)

# --- العمود الأيمن ---
with right_col:
    # مكان الكاميرا (Placeholder حاليًا)
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)")
    st.write("")
    st.markdown("<div class='box'>نتيجة الإشارة ستظهر هنا</div>", unsafe_allow_html=True)
