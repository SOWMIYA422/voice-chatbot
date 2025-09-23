import streamlit as st
import os
import json
from llm_runner import LocalLLM
from gtts import gTTS  # ✅ Added for TTS

st.set_page_config(page_title="🎙️ Live Voice Chatbot", layout="wide")

# === Custom Background with Avatar + Bounce ===
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #fbc2eb, #a18cd1, #fbc2eb, #ffdde1);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
    position: relative;
}
[data-testid="stSidebar"] {
    background: rgba(25, 25, 40, 0.95);
}
h1, h2, h3, h4, h5, h6, p, span, label {
    color: white !important;
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 120px;
    height: 120px;
    background-image: url('https://cdn-icons-png.flaticon.com/512/4712/4712109.png');
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.9;
    animation: bounce 3s ease-in-out infinite;
    pointer-events: none;
}
@keyframes bounce {
    0%, 100% {transform: translateY(0px);}
    50% {transform: translateY(-12px);}
}
.stTextInput, .stButton button, textarea {
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.15);
    border: none;
    color: white;
    padding: 10px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# === Sidebar Info ===
st.sidebar.title("🎙️ Live Voice Q&A")
st.sidebar.write(
    "Run `python stt_worker.py` in another terminal to start live transcription."
)

# === Transcript Data Folder ===
TRANSCRIPT_DIR = "transcriptdata"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


def get_latest_transcript():
    files = [f for f in os.listdir(TRANSCRIPT_DIR) if f.endswith(".txt")]
    if not files:
        return None
    latest = max(files, key=lambda f: os.path.getctime(os.path.join(TRANSCRIPT_DIR, f)))
    return os.path.join(TRANSCRIPT_DIR, latest)


def load_cache(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(json_path, cache):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def answer_query(query, llm):
    transcript_file = get_latest_transcript()
    if not transcript_file:
        return "No transcript found."

    base = os.path.splitext(transcript_file)[0]
    json_path = base + ".json"
    cache = load_cache(json_path)

    if query in cache:
        return cache[query]

    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    if not transcript_text.strip():
        return "Transcript is empty."

    prompt = f"""You are a helpful assistant.
Answer the user's question ONLY from the transcript below.
- If the answer is not in the transcript, reply exactly: "out of audio details".
- Do NOT include unrelated transcript text.
- Give a short, direct answer.

Transcript:
{transcript_text}

Question: {query}
Answer:"""

    answer = llm.ask(prompt)
    cache[query] = answer
    save_cache(json_path, cache)
    return answer


# === UI Tabs ===
tab1, tab2 = st.tabs(["📝 Live Transcription", "🤖 LLM Q&A"])

# --- Tab 1: Live Transcript ---
with tab1:
    st.subheader("Recent Transcript")
    transcript_file = get_latest_transcript()
    if transcript_file:
        with open(transcript_file, "r", encoding="utf-8") as f:
            content = f.read()
        st.text_area("Transcript", content, height=400)
    else:
        st.write("No transcripts found yet.")

# --- Tab 2: Q&A ---
with tab2:
    st.subheader("Ask a Question")
    question = st.text_input("Your question")
    if st.button("Ask LLM"):
        llm = LocalLLM()
        answer = answer_query(question, llm)

        st.write("### 🤖 Answer")
        st.write(answer)

        # === 🔊 Text-to-Speech ===
        try:
            tts = gTTS(answer, lang="en")

            # Save TTS file alongside transcript
            transcript_file = get_latest_transcript()
            if transcript_file:
                base = os.path.splitext(transcript_file)[0]
                tts_file = base + "_answer.mp3"
            else:
                tts_file = os.path.join(TRANSCRIPT_DIR, "answer.mp3")

            tts.save(tts_file)

            # Play audio inside Streamlit
            with open(tts_file, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")

            st.success(f"🔊 Answer saved as {tts_file}")
        except Exception as e:
            st.error(f"TTS error: {e}")
