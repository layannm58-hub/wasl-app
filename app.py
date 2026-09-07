import streamlit as st
import streamlit.components.v1 as components
import json

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

    .box-notes {
        background-color: #676279;
        border-radius: 10px;
        padding: 16px;
        min-height: 40vh;
        margin-top: 16px;
    }
    .box-notes hr { border-color: white; margin: 8px 0; }

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

# ===== قاموس الكلمات الطبية =====
SIGN_DATA = {
    "headache":  {"label": "صداع",       "video": "signs/headache.mp4",  "keywords": ["صداع"]},
    "pain":      {"label": "ألم",         "video": "signs/pain.mp4",      "keywords": ["ألم", "الم"]},
    "stomach":   {"label": "بطن",         "video": "signs/stomach.mp4",   "keywords": ["بطن"]},
    "nausea":    {"label": "غثيان",       "video": "signs/nausea.mp4",    "keywords": ["غثيان"]},
    "dizziness": {"label": "دوخة / دوار", "video": "signs/dizziness.mp4", "keywords": ["دوخة", "دوار"]},
}

NO_SELECTION = "-- اختر عبارة --"
options = [NO_SELECTION] + [v["label"] for v in SIGN_DATA.values()]
label_to_key = {v["label"]: k for k, v in SIGN_DATA.items()}

# ===== قراءة الكلمة المكتشفة تلقائيًا من رابط الصفحة (لو موجودة) =====
detected_key = st.query_params.get("word", "")
default_index = 0
if detected_key in SIGN_DATA:
    default_index = options.index(SIGN_DATA[detected_key]["label"])

# ===== الأعمدة (36% / 56%) =====
left_col, right_col = st.columns([36, 56])

with left_col:
    with st.container(border=True):
        selected_word = st.selectbox(
            "اختاري العبارة الطبية:",
            options=options,
            index=default_index,
            label_visibility="collapsed"
        )

        selected_key = label_to_key.get(selected_word)
        if selected_key:
            st.video(SIGN_DATA[selected_key]["video"])
            st.markdown(f"<div class='sign-label'>{SIGN_DATA[selected_key]['label']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='sign-label'>✋ سيظهر فيديو الإشارة هنا تلقائيًا عند التحدث، أو اختاري يدويًا</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='box-notes'>
            <b>Patient Notes:</b><hr>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)", label_visibility="collapsed")

    # ===== Speech-to-Text مع الكشف التلقائي عن الكلمات الطبية =====
    keywords_js = json.dumps({k: v["keywords"] for k, v in SIGN_DATA.items()})

    speech_html = f"""
    <div style="background-color:#12082d; border:1px solid white; border-radius:10px;
                padding:16px; font-family:'Times New Roman',serif; color:white; min-height:26vh; margin-top:16px;">
      <button id="micBtn" style="background-color:#508782; border:none; border-radius:20px;
              padding:8px 24px; color:white; font-family:'Times New Roman',serif;
              font-size:16px; cursor:pointer;">🎙️ تحدث الآن</button>
      <p id="output" style="margin-top:16px; font-size:18px;">النص سيظهر هنا...</p>
      <script>
      const micBtn = document.getElementById('micBtn');
      const output = document.getElementById('output');
      const SIGN_KEYWORDS = {keywords_js};
      let recognition;

      function findMatch(text) {{
          for (const key in SIGN_KEYWORDS) {{
              const words = SIGN_KEYWORDS[key];
              for (const w of words) {{
                  if (text.includes(w)) {{
                      return key;
                  }}
              }}
          }}
          return null;
      }}

      if ('webkitSpeechRecognition' in window) {{
          recognition = new webkitSpeechRecognition();
          recognition.lang = 'ar-SA';
          recognition.continuous = false;
          recognition.interimResults = false;

          recognition.onresult = function(event) {{
              const text = event.results[0][0].transcript;
              output.innerText = text;

              const matchedKey = findMatch(text);
              if (matchedKey) {{
                  const url = new URL(window.parent.location.href);
                  url.searchParams.set('word', matchedKey);
                  window.parent.location.href = url.toString();
              }}
          }};
          recognition.onerror = function(event) {{
              output.innerText = "حدث خطأ: " + event.error;
          }};
      }} else {{
          output.innerText = "المتصفح لا يدعم هذه الميزة، جربي Google Chrome.";
      }}

      micBtn.onclick = function() {{
          output.innerText = "... يستمع الآن";
          recognition.start();
      }};
      </script>
    </div>
    """
    components.html(speech_html, height=280)
