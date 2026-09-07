import streamlit as st
import streamlit.components.v1 as components

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
        padding: 16px;
        min-height: 55vh;
    }
    .box-notes hr { border-color: white; margin: 8px 0; }
    .top-left-box {
        min-height: 55vh;
    }
    .sign-label {
        text-align: center;
        color: #cfcfe8;
        font-size: 15px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ===== الشريط العلوي =====
st.markdown("""
    <div class='header-frame'>
        <div class='header-spacer'></div>
        <div class='room-no-pill'>Room no</div>
        <div class='wasl-logo'><b style='font-size:20px;'>WASL</b><br>وَصل</div>
    </div>
""", unsafe_allow_html=True)

# ===== قاموس الكلمات وفيديوهات لغة الإشارة =====
# اسم الملف داخل مجلد signs/ لكل عبارة طبية
SIGN_VIDEOS = {
    "-- اختر عبارة --": None,
    "صداع": "signs/headache.mp4",
    "ألم": "signs/pain.mp4",
    "بطن": "signs/stomach.mp4",
    "غثيان": "signs/nausea.mp4",
    "دوخة / دوار": "signs/dizziness.mp4",
}

# ===== الأعمدة (36% / 56%) =====
left_col, right_col = st.columns([36, 56])

with left_col:
    st.markdown("<div class='box top-left-box'>", unsafe_allow_html=True)

    selected_word = st.selectbox(
        "اختاري العبارة الطبية:",
        options=list(SIGN_VIDEOS.keys()),
        label_visibility="collapsed"
    )

    video_path = SIGN_VIDEOS[selected_word]
    if video_path:
        st.video(video_path)
        st.markdown(f"<div class='sign-label'>{selected_word}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='sign-label'>✋ اختاري عبارة لعرض فيديو لغة الإشارة</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='box-notes'>
            <b>Patient Notes:</b><hr>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)", label_visibility="collapsed")

    # ===== Speech-to-Text =====
    speech_html = """
    <div style="background-color:#12082d; border:1px solid white; border-radius:10px;
                padding:16px; font-family:'Times New Roman',serif; color:white; min-height:26vh; margin-top:16px;">
      <button id="micBtn" style="background-color:#508782; border:none; border-radius:20px;
              padding:8px 24px; color:white; font-family:'Times New Roman',serif;
              font-size:16px; cursor:pointer;">🎙️ تحدث الآن</button>
      <p id="output" style="margin-top:16px; font-size:18px;">النص سيظهر هنا...</p>
      <script>
      const micBtn = document.getElementById('micBtn');
      const output = document.getElementById('output');
      let recognition;

      if ('webkitSpeechRecognition' in window) {
          recognition = new webkitSpeechRecognition();
          recognition.lang = 'ar-SA';
          recognition.continuous = false;
          recognition.interimResults = false;

          recognition.onresult = function(event) {
              const text = event.results[0][0].transcript;
              output.innerText = text;
          };
          recognition.onerror = function(event) {
              output.innerText = "حدث خطأ: " + event.error;
          };
      } else {
          output.innerText = "المتصفح لا يدعم هذه الميزة، جربي Google Chrome.";
      }

      micBtn.onclick = function() {
          output.innerText = "... يستمع الآن";
          recognition.start();
      };
      </script>
    </div>
    """
    components.html(speech_html, height=280)
