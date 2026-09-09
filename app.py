"""
app.py - WASL (النسخة المدمجة الكاملة)
تصميم الموقع + لغة الإشارة + Patient Notes + كاميرا التعرف الذكية
+ الموافقة قبل تشغيل الكاميرا + تحويل كلام الطبيب لنص + شاشة ما يظهر للمريض

ملاحظة تقنية: استخدمنا @st.fragment بدل حلقة while القديمة، عشان تفضل كل
الأزرار (زر "تحدث الآن"، القائمة المنسدلة، البحث) شغّالة وتستجيب أثناء
تشغيل الكاميرا. يحتاج Streamlit نسخة 1.33 أو أحدث (شغّال غالبًا عندك).
"""

import os
import time
import cv2
import joblib
import numpy as np
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import av

from collections import Counter, deque
from threading import Lock

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import mediapipe as mp

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

st.set_page_config(page_title="WASL - وَصل", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "wasl_model.pkl")
METADATA_PATH = os.path.join(BASE_DIR, "wasl_metadata.pkl")
LANDMARKER_PATH = os.path.join(BASE_DIR, "models", "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

NUM_LANDMARKS = 21
FEATURES_PER_HAND = NUM_LANDMARKS * 3

CAMERA_LABEL_TO_ARABIC = {
    "alam": "ألم",
    "sudaa": "صداع",
    "batn": "ألم بطن",
    "dawkha": "دوخة",
    "ghathayan": "غثيان",
}

STABILITY_WINDOW = 6
STABILITY_THRESHOLD = 3
MIN_CONFIDENCE = 0.45

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# ============================================================
# التنسيقات (CSS الكامل من تصميم لينا)
# ============================================================
st.markdown("""
    <style>
    .stApp {
        background-color: #12082d;
        color: white;
        font-family: 'Times New Roman', Times, serif, 'Segoe UI Emoji', 'Noto Color Emoji', 'Segoe UI Symbol';
    }
    button p, button div, button span {
        font-family: 'Times New Roman', Times, serif, 'Segoe UI Emoji', 'Noto Color Emoji', 'Segoe UI Symbol' !important;
    }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    [data-testid="stHorizontalBlock"] { gap: 1.5rem; }
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
    .wasl-logo { flex: 1; text-align: right; color: #508782; line-height: 1.3; }

    .sign-label { text-align: center; color: #cfcfe8; font-size: 15px; margin-top: 8px; }
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
        background-color: #508782;
        color: #ffffff;
        border: 2px solid #3a6864;
        border-radius: 10px;
        padding: 24px;
        margin-top: 16px;
        text-align: center;
    }
    .patient-view-title { font-size: 14px; color: #ffffff; margin-bottom: 10px; font-weight: bold; }
    .patient-view-text { font-size: 32px; font-weight: bold; line-height: 1.4; }
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

# ============================================================
# قاموس الكلمات الطبية (فيديو لغة الإشارة)
# ============================================================
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


# ============================================================
# حالة الجلسة (Session State)
# ============================================================
if "detected_key" not in st.session_state:
    st.session_state["detected_key"] = None
if "listening" not in st.session_state:
    st.session_state["listening"] = False
if "last_transcript" not in st.session_state:
    st.session_state["last_transcript"] = ""
if "camera_consent" not in st.session_state:
    st.session_state["camera_consent"] = False
if "patient_lookup" not in st.session_state:
    st.session_state["patient_lookup"] = None

NO_SELECTION = "-- اختر عبارة --"
options = [NO_SELECTION] + [v["label"] for v in SIGN_DATA.values()]
label_to_key = {v["label"]: k for k, v in SIGN_DATA.items()}
key_to_label = {k: v["label"] for k, v in SIGN_DATA.items()}


# ============================================================
# تحميل النموذج + إعداد الكاميرا (mediapipe HandLandmarker)
# ============================================================
@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    return model, metadata


def create_landmarker():
    base_options = mp_python.BaseOptions(model_asset_path=LANDMARKER_PATH)
    options_lm = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        running_mode=vision.RunningMode.IMAGE,
    )
    return vision.HandLandmarker.create_from_options(options_lm)


def extract_features(detection_result):
    left = [0.0] * FEATURES_PER_HAND
    right = [0.0] * FEATURES_PER_HAND
    num_hands = 0
    if detection_result.hand_landmarks:
        num_hands = len(detection_result.hand_landmarks)
        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            flat = []
            for lm in hand_landmarks:
                flat.extend([lm.x, lm.y, lm.z])
            handed = detection_result.handedness[idx][0].category_name
            if handed == "Left":
                left = flat
            elif handed == "Right":
                right = flat
    return np.array(left + right, dtype=np.float32).reshape(1, -1), num_hands


def draw_landmarks(img, detection_result):
    h, w, _ = img.shape
    if not detection_result.hand_landmarks:
        return img
    for hand_landmarks in detection_result.hand_landmarks:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        for s, e in HAND_CONNECTIONS:
            cv2.line(img, points[s], points[e], (255, 255, 255), 1)
        for p in points:
            cv2.circle(img, p, 3, (0, 200, 255), -1)
    return img


FRAME_SKIP = 2  # يشغّل الكشف الثقيل كل 3 إطارات بس (1 من كل 3)، والباقي يعرض آخر نتيجة محفوظة


class WaslVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.lock = Lock()
        self.model, self.metadata = load_model()
        self.landmarker = create_landmarker()
        self.history = deque(maxlen=STABILITY_WINDOW)
        self.result_label = "لا يوجد يد"
        self.confidence = 0.0
        self.num_hands = 0
        self.frame_counter = 0
        self.last_detection_result = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        self.frame_counter += 1
        run_detection = (self.frame_counter % (FRAME_SKIP + 1) == 0)

        if run_detection:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            detection_result = self.landmarker.detect(mp_image)
            self.last_detection_result = detection_result
        else:
            detection_result = self.last_detection_result

        if detection_result is None:
            cv2.putText(img, "Hands: 0", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        features, num_hands = extract_features(detection_result)
        img = draw_landmarks(img, detection_result)

        if run_detection:
            if num_hands > 0:
                proba = self.model.predict_proba(features)[0]
                pred_idx = int(np.argmax(proba))
                pred_label = self.model.classes_[pred_idx]
                pred_conf = float(proba[pred_idx])
                self.history.append(pred_label)
                most_common_label, count = Counter(self.history).most_common(1)[0]

                if count >= STABILITY_THRESHOLD and pred_conf >= MIN_CONFIDENCE:
                    stable = most_common_label
                else:
                    stable = None

                with self.lock:
                    self.num_hands = num_hands
                    self.confidence = pred_conf
                    if stable:
                        self.result_label = CAMERA_LABEL_TO_ARABIC.get(stable, stable)
                    else:
                        self.result_label = "جاري التعرف..."
            else:
                self.history.clear()
                with self.lock:
                    self.num_hands = 0
                    self.confidence = 0.0
                    self.result_label = "لا يوجد يد"

        cv2.putText(img, f"Hands: {num_hands}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ============================================================
# التخطيط: عمود 36% (الإشارة + بيانات المريض) / عمود 56% (الكاميرا + الصوت)
# ============================================================
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
            label_visibility="collapsed",
        )

        selected_key = label_to_key.get(selected_word)
        if selected_key:
            st.video(SIGN_DATA[selected_key]["video"])
            st.markdown(f"<div class='sign-label'>{SIGN_DATA[selected_key]['label']}</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div style='text-align:center; font-size:11px; color:#8a8aa8; margin-top:4px;'>"
                "المصدر: الجمعية السعودية للإعاقة السمعية (sshi.sa)</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='sign-label'>✋ سيظهر الفيديو هنا تلقائيًا فور تحدث الطبيب</div>",
                        unsafe_allow_html=True)

        st.markdown(
            "<div class='review-badge'>⚕️ ترجمة مقترحة — يُرجى من الكادر الصحي التأكد منها قبل اتخاذ أي قرار</div>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown("**Patient Notes**")

        MOCK_PATIENTS = {
            "1111111111": {"name_ar": "محمد أحمد", "name_en": "Mohammed Ahmed", "age": 45,
                           "gender_ar": "ذكر", "gender_en": "Male", "blood_type": "O+",
                           "chronic_ar": "سكري، ضغط", "chronic_en": "Diabetes, Hypertension",
                           "allergy_ar": "لا يوجد", "allergy_en": "None", "room": "204"},
            "2222222222": {"name_ar": "سارة علي", "name_en": "Sarah Ali", "age": 32,
                           "gender_ar": "أنثى", "gender_en": "Female", "blood_type": "A+",
                           "chronic_ar": "لا يوجد", "chronic_en": "None",
                           "allergy_ar": "بنسلين", "allergy_en": "Penicillin", "room": "108"},
            "3333333333": {"name_ar": "خالد ناصر", "name_en": "Khalid Nasser", "age": 60,
                           "gender_ar": "ذكر", "gender_en": "Male", "blood_type": "B-",
                           "chronic_ar": "قصور كلوي", "chronic_en": "Kidney Failure",
                           "allergy_ar": "لا يوجد", "allergy_en": "None", "room": "312"},
        }

        id_input = st.text_input("رقم الهوية:", key="patient_id_input", placeholder="مثال: 1111111111")

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
                rows_html += (
                    "<div style='display:flex; justify-content:space-between; align-items:center; "
                    "padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.15);'>"
                    f"<span style='text-align:right;'><b>{ar_label}:</b> {ar_value}</span>"
                    f"<span style='font-size:13px; color:#9a9ab8; text-align:left;'>{en_label}: {en_value}</span>"
                    "</div>"
                )
            st.markdown(f"<div style='direction:rtl;'>{rows_html}</div>", unsafe_allow_html=True)
            st.caption("⚠️ بيانات افتراضية لأغراض العرض التوضيحي فقط")
        elif id_input:
            st.warning("لا يوجد مريض بهذا الرقم (جربي: 1111111111 / 2222222222 / 3333333333)")

with right_col:
    # ===== الموافقة قبل تشغيل الكاميرا =====
    if not st.session_state["camera_consent"]:
        st.markdown(
            "<div class='consent-box'>"
            "🔒 <b>قبل تشغيل الكاميرا:</b> يُستخدم البث المرئي فقط لترجمة لغة الإشارة لحظيًا، "
            "ولا يتم تسجيل أو تخزين أي فيديو أو صورة للمريض. "
            "يُرجى التأكد من أخذ موافقة المريض أو مرافقه قبل المتابعة."
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("✅ تم الحصول على الموافقة — تشغيل الكاميرا"):
            st.session_state["camera_consent"] = True
            st.rerun()
    else:
        ctx = webrtc_streamer(
            key="wasl-camera",
            video_processor_factory=WaslVideoProcessor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={
                "video": {"width": {"ideal": 480}, "height": {"ideal": 360}},
                "audio": False,
            },
            async_processing=True,
        )

        st.markdown("---")

        @st.fragment(run_every=0.3)
        def show_camera_result():
            if ctx.video_processor:
                with ctx.video_processor.lock:
                    label = ctx.video_processor.result_label
                    conf = ctx.video_processor.confidence
                    n_hands = ctx.video_processor.num_hands
                st.markdown(
                    f"""
                    <div style='text-align:center; padding:20px; border:1px solid white; border-radius:10px;'>
                        <h1 style='margin:0; color:white;'>{label}</h1>
                        <p style='color:#9a9ab8;'>الثقة: {conf * 100:.1f}% | الأيدي: {n_hands}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='text-align:center; padding:20px; border:1px solid white; border-radius:10px;'>"
                    "<p style='color:#9a9ab8;'>بانتظار تشغيل الكاميرا...</p></div>",
                    unsafe_allow_html=True,
                )

        show_camera_result()

    # ===== تحويل كلام الطبيب لنص =====
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

    # ===== ما يظهر للمريض =====
    patient_text = st.session_state["last_transcript"] or "سيظهر كلام الطبيب هنا..."
    st.markdown(
        f"""
        <div class='patient-view-box'>
            <div class='patient-view-title'>👤 ما يظهر للمريض</div>
            <div class='patient-view-text'>{patient_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
