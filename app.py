import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="WASL - وَصل", layout="wide")

st.markdown("""
    <style>


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
    .review-badge {
        text-align: center;
        background-color: #3a2f57;
        border: 1px solid #8a8ab0;
        border-radius: 6px;
        color: #e6c46b;
        font-size: 13px;
        padding: 6px 10px;
        margin-top: 6px;
    }
    .consent-box {
        background-color: #241a3d;
        border: 1px solid #8a8ab0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
        font-size: 14px;
        color: #e6e6f2;
    }
    .speech-box {
        background-color: #12082d;
        border: 1px solid white;
        border-radius: 10px;
        padding: 16px;
        margin-top: 16px;
    }
    .patient-view-box {
        background-color: #f2eefa;
        color: #12082d;
        border: 2px solid #7a6ba8;
        border-radius: 10px;
        padding: 24px;
        margin-top: 16px;
        text-align: center;
    }
    .patient-view-title {
        font-size: 14px;
        color: #508782;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .patient-view-text {
        font-size: 32px;
        font-weight: bold;
        line-height: 1.4;
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
    "headache":   {"label": "صداع",              "video": "signs/headache.mp4"},
    "pain":       {"label": "ألم",                "video": "signs/pain.mp4"},
    "stomach":    {"label": "بطن",                "video": "signs/stomach.mp4"},
    "nausea":     {"label": "غثيان",              "video": "signs/nausea.mp4"},
    "dizziness":  {"label": "دوخة / دوار",        "video": "signs/dizziness.mp4"},
    "how_health": {"label": "كيف صحتك؟",          "video": "signs/how_health.mp4"},
    "check_look": {"label": "هل لي أن ألقي نظرة؟", "video": "signs/check_look.mp4"},
}
SIGN_KEYWORDS = {
    "headache": ["صداع"],
    "pain": ["الم"],
    "stomach": ["بطن"],
    "nausea": ["غثيان"],
    "dizziness": ["دوخه", "دوار"],
    "how_health": ["صحتك", "كيف صحتك"],
    "check_look": ["القي نظره", "ألقي نظرة", "اشوف", "اعاينك"],
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
if "camera_consent" not in st.session_state:
    st.session_state["camera_consent"] = False

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
            st.markdown("<div style='text-align:center; font-size:11px; color:#8a8aa8; margin-top:4px;'>المصدر: الجمعية السعودية للإعاقة السمعية (sshi.sa)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='sign-label'>✋ سيظهر الفيديو هنا تلقائيًا فور تحدث الطبيب</div>", unsafe_allow_html=True)

        # تنويه: النتيجة مقترحة وتتطلب مراجعة الكادر الصحي، وليست تشخيصًا نهائيًا
        st.markdown(
            "<div class='review-badge'>⚕️ ترجمة مقترحة — يُرجى من الكادر الصحي التأكد منها قبل اتخاذ أي قرار</div>",
            unsafe_allow_html=True
        )

    with st.container(border=True):
        st.markdown("**Patient Notes**")

        MOCK_PATIENTS = {
            "1111111111": {
                "name_ar": "محمد أحمد", "name_en": "Mohammed Ahmed",
                "age": 45,
                "gender_ar": "ذكر", "gender_en": "Male",
                "blood_type": "O+",
                "chronic_ar": "سكري، ضغط", "chronic_en": "Diabetes, Hypertension",
                "allergy_ar": "لا يوجد", "allergy_en": "None",
                "room": "204",
            },
            "2222222222": {
                "name_ar": "سارة علي", "name_en": "Sarah Ali",
                "age": 32,
                "gender_ar": "أنثى", "gender_en": "Female",
                "blood_type": "A+",
                "chronic_ar": "لا يوجد", "chronic_en": "None",
                "allergy_ar": "بنسلين", "allergy_en": "Penicillin",
                "room": "108",
            },
            "3333333333": {
                "name_ar": "خالد ناصر", "name_en": "Khalid Nasser",
                "age": 60,
                "gender_ar": "ذكر", "gender_en": "Male",
                "blood_type": "B-",
                "chronic_ar": "قصور كلوي", "chronic_en": "Kidney Failure",
                "allergy_ar": "لا يوجد", "allergy_en": "None",
                "room": "312",
            },
        }

        if "patient_lookup" not in st.session_state:
            st.session_state["patient_lookup"] = None

        id_input = st.text_input(
            "رقم الهوية:",
            key="patient_id_input",
            placeholder="مثال: 1111111111"
        )

        if st.button("🔍 بحث"):
            st.session_state["patient_lookup"] = MOCK_PATIENTS.get(id_input.strip())

        result = st.session_state["patient_lookup"]
        if result:
            fields = [
                ("الاسم", "Name", result['name_ar'], result['name_en']),
                ("العمر", "Age", result['age'], result['age']),
                ("الجنس", "Gender", result['gender_ar'], result['gender_en']),
                ("فصيلة الدم", "Blood Type", result['blood_type'], result['blood_type']),
                ("الأمراض المزمنة", "Chronic Conditions", result['chronic_ar'], result['chronic_en']),
                ("الحساسية", "Allergy", result['allergy_ar'], result['allergy_en']),
                ("رقم الغرفة", "Room No", result['room'], result['room']),
            ]
            rows_html = ""
            for ar_label, en_label, ar_value, en_value in fields:
                row = ("<div style='display:flex; justify-content:space-between; align-items:center; "
                       "padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.15);'>"
                       f"<span style='text-align:right;'><b>{ar_label}:</b> {ar_value}</span>"
                       f"<span style='font-size:13px; color:#9a9ab8; text-align:left;'>{en_label}: {en_value}</span>"
                       "</div>")
                rows_html += row
            full_html = "<div style='direction:rtl;'>" + rows_html + "</div>"
            st.markdown(full_html, unsafe_allow_html=True)
            st.caption("⚠️ بيانات افتراضية لأغراض العرض التوضيحي فقط")
        elif id_input:
            st.warning("لا يوجد مريض بهذا الرقم (جربي: 1111111111 / 2222222222 / 3333333333)")

with right_col:
    # ===== تنويه الموافقة قبل تفعيل الكاميرا =====
    if not st.session_state["camera_consent"]:
        st.markdown(
            "<div class='consent-box'>"
            "🔒 <b>قبل تشغيل الكاميرا:</b> يُستخدم البث المرئي فقط لترجمة لغة الإشارة لحظيًا، "
            "ولا يتم تسجيل أو تخزين أي فيديو أو صورة للمريض. "
            "يُرجى التأكد من أخذ موافقة المريض أو مرافقه قبل المتابعة."
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("✅ تم الحصول على الموافقة — تشغيل الكاميرا"):
            st.session_state["camera_consent"] = True
            st.rerun()
    else:
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

    # ===== ما يظهر للمريض (نفس النص، بخط كبير وواضح) =====
    patient_text = st.session_state["last_transcript"] or "سيظهر كلام الطبيب هنا..."
    st.markdown(
        f"""
        <div class='patient-view-box'>
            <div class='patient-view-title'>👤 ما يظهر للمريض</div>
            <div class='patient-view-text'>{patient_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
