import streamlit as st
from streamlit_js_eval import streamlit_js_eval

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
    .speech-box {
        background-color: #12082d;
        border: 1px solid white;
        border-radius: 10px;
        padding: 16px;
        margin-top: 16px;
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
    "headache":  {"label": "صداع",       "video": "signs/headache.mp4"},
    "pain":      {"label": "ألم",         "video": "signs/pain.mp4"},
    "stomach":   {"label": "بطن",         "video": "signs/stomach.mp4"},
    "nausea":    {"label": "غثيان",       "video": "signs/nausea.mp4"},
    "dizziness": {"label": "دوخة / دوار", "video": "signs/dizziness.mp4"},
}
SIGN_KEYWORDS = {
    "headache": ["صداع"],
    "pain": ["الم"],
    "stomach": ["بطن"],
    "nausea": ["غثيان"],
    "dizziness": ["دوخه", "دوار"],
}


def normalize_arabic(text: str) -> str:
    text = text or ""
    for ch in "إأآا":
        text = text.replace(ch, "ا")
    text = text.replace("ى", "ي").replace("ة", "ه")
    text = "".join(c for c in text if not ("\u064B" <= c <= "\u0652"))
    text = text.replace("ـ", "")
    return " ".join(text.split()).strip()


def find_match(transcript: str):
    norm_text = normalize_arabic(transcript)
    for key, words in SIGN_KEYWORDS.items():
        for w in words:
            if normalize_arabic(w) in norm_text:
                return key
    return None


if "detected_key" not in st.session_state:
    st.session_state["detected_key"] = None
if "listening" not in st.session_state:
    st.session_state["listening"] = False
if "last_transcript" not in st.session_state:
    st.session_state["last_transcript"] = ""

NO_SELECTION = "-- اختر عبارة --"
options = [NO_SELECTION] + [v["label"] for v in SIGN_DATA.values()]
label_to_key = {v["label"]: k for k, v in SIGN_DATA.items()}
key_to_label = {k: v["label"] for k, v in SIGN_DATA.items()}

# ===== الأعمدة (36% / 56%) =====
left_col, right_col = st.columns([36, 56])

with left_col:
    with st.container(border=True):
        default_index = 0
        if st.session_state["detected_key"] in SIGN_DATA:
            default_index = options.index(key_to_label[st.session_state["detected_key"]])

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
            st.markdown("<div class='sign-label'>✋ سيظهر الفيديو هنا تلقائيًا فور تحدث الطبيب</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='box-notes'>
            <b>Patient Notes:</b><hr>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    camera_photo = st.camera_input("مكان الكاميرا (مؤقت)", label_visibility="collapsed")

    st.markdown("<div class='speech-box'>", unsafe_allow_html=True)

    if st.button("🎙️ تحدث الآن"):
        st.session_state["listening"] = True

    if st.session_state["listening"]:
        transcript = streamlit_js_eval(
            js_expressions="""
            new Promise((resolve) => {
                try {
                    const recognition = new webkitSpeechRecognition();
                    recognition.lang = 'ar-SA';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.onresult = function(event) {
                        resolve(event.results[0][0].transcript);
                    };
                    recognition.onerror = function(event) {
                        resolve('ERROR:' + event.error);
                    };
                    recognition.start();
                } catch (e) {
                    resolve('ERROR:' + e.message);
                }
            })
            """,
            key="speech_js",
            want_output=True,
        )

        if transcript is not None:
            st.session_state["listening"] = False
            if isinstance(transcript, str) and not transcript.startswith("ERROR"):
                st.session_state["last_transcript"] = transcript
                matched = find_match(transcript)
                if matched:
                    st.session_state["detected_key"] = matched
            st.rerun()

    if st.session_state["last_transcript"]:
        st.markdown(f"**النص:** {st.session_state['last_transcript']}")
    else:
        st.markdown("النص سيظهر هنا بعد الضغط والتحدث...")

    st.markdown("</div>", unsafe_allow_html=True)
