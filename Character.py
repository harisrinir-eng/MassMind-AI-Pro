import streamlit as st
import ollama
import time
import os
import uuid
from gtts import gTTS

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="MassMind AI Pro",
    layout="wide"
)

# -----------------------------
# SESSION MEMORY INIT
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------
with st.sidebar:
    st.header("🎬 Control Panel")

    chat_mode = st.radio("Chat Mode", ["Thalapathy Cinematic 🎬", "Normal Chat 💬"])
    mode = st.radio("Mode", ["Master 🎓", "Leo 🐺", "Ghilli ⚡", "Coach 🧠"])
    language = st.radio("Language", ["English", "Tamil", "Mix"])
    emotion = st.selectbox("Emotion Style", ["Mass 🔥", "Dark 😈", "Funny 😎", "Motivational 💪"])
    short_mode = st.toggle("⚡ Ultra Short Reply", value=True)
    auto_punch = st.toggle("🎯 Auto Punch Ending", value=True)
    voice_enabled = st.toggle("🔊 Voice")
    temperature = st.slider("Mass Level 🔥", 0.0, 1.5, 1.0, 0.1)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# BACKGROUND BASED ON MODE
# -----------------------------
def get_background(mode):
    if "Master" in mode:
        return "linear-gradient(-45deg, #1a0000, #330000, #660000, #000000)"
    elif "Leo" in mode:
        return "linear-gradient(-45deg, #000000, #1a0000, #330000, #000000)"
    elif "Ghilli" in mode:
        return "linear-gradient(-45deg, #001f3f, #ff851b, #001f3f, #ff4136)"
    elif "Coach" in mode:
        return "linear-gradient(-45deg, #1a0033, #330066, #660099, #000000)"

bg_style = get_background(mode)

# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
.stApp {{
    background: {bg_style};
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}}

@keyframes gradientBG {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

.title {{
    text-align: center;
    font-size: 60px;
    font-weight: bold;
    color: #ffcc00;
    animation: glow 2s infinite alternate;
}}

@keyframes glow {{
    from {{ text-shadow: 0 0 10px red; }}
    to {{ text-shadow: 0 0 35px gold; }}
}}

.animated-reply {{
    animation: fadeSlide 0.6s ease-out forwards,
               glowPulse 1.5s ease-in-out;
    padding: 15px;
    border-radius: 15px;
    background: rgba(255, 204, 0, 0.08);
    border: 1px solid rgba(255, 204, 0, 0.4);
}}

@keyframes fadeSlide {{
    from {{ opacity: 0; transform: translateY(25px) scale(0.95); }}
    to {{ opacity: 1; transform: translateY(0px) scale(1); }}
}}

@keyframes glowPulse {{
    0% {{ box-shadow: 0 0 0px gold; }}
    50% {{ box-shadow: 0 0 25px gold; }}
    100% {{ box-shadow: 0 0 0px gold; }}
}}

/* Punch explosion */
.flash {{
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    background: rgba(255,215,0,0.3);
    animation: flashAnim 0.4s ease;
    pointer-events:none;
}}

@keyframes flashAnim {{
    from {{opacity:1;}}
    to {{opacity:0;}}
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.markdown('<div class="title">🔥 MassMind AI Pro 🔥</div>', unsafe_allow_html=True)

# -----------------------------
# PERSONA BUILDER
# -----------------------------
def build_persona():
    if chat_mode == "Normal Chat 💬":
        return "You are a helpful AI assistant. Answer clearly and politely."

    persona = ""
    if "Master" in mode:
        persona = "You are Vijay from Master. Bold professor tone."
    elif "Leo" in mode:
        persona = "You are Vijay from Leo. Dark and intense."
    elif "Ghilli" in mode:
        persona = "You are energetic Vijay from Ghilli."
    elif "Coach" in mode:
        persona = "You are Thalapathy Vijay as a powerful life coach."

    persona += f" Emotion style: {emotion}."

    if language == "Tamil":
        persona += " Reply fully in Tamil."
    elif language == "Mix":
        persona += " Reply in Tamil-English mixed style."

    if short_mode:
        persona += " Maximum 3 lines only."

    if auto_punch:
        persona += " End with one short mass punch line."
    return persona

# -----------------------------
# QUICK BUTTONS (Cinematic only)
# -----------------------------
if chat_mode != "Normal Chat 💬":
    st.subheader("⚡ Quick Fire")
    col1, col2, col3 = st.columns(3)
    if col1.button("🔥 Motivate Me"): st.session_state.quick_prompt = "Motivate me strongly."
    if col2.button("😈 Roast Me"): st.session_state.quick_prompt = "Roast me in mass style."
    if col3.button("🎬 Give Punch"): st.session_state.quick_prompt = "Give one powerful punch dialogue."

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# CHAT INPUT
# -----------------------------
user_input = st.chat_input("Speak to Thalapathy..." if chat_mode != "Normal Chat 💬" else "Ask me anything...")

if "quick_prompt" in st.session_state:
    user_input = st.session_state.quick_prompt
    del st.session_state.quick_prompt

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.write(user_input)

    full_messages = [{"role":"system","content":build_persona()}] + st.session_state.messages

    with st.chat_message("assistant"):
        loader = st.empty()
        loader.markdown("🔥 Charging Mass Energy..." if chat_mode != "Normal Chat 💬" else "💬 Thinking...")
        time.sleep(0.8)

        response = ollama.chat(
            model="gemma3:4b",
            messages=full_messages,
            options={"temperature": temperature, "num_predict": 120}
        )

        reply = response["message"]["content"]
        loader.empty()

        # -----------------------------
        # Animated reply for BOTH modes
        # -----------------------------
        animated_container = st.empty()
        display_text = ""
        for char in reply:
            display_text += char
            animated_container.markdown(f'<div class="animated-reply">{display_text}</div>', unsafe_allow_html=True)
            time.sleep(0.002)

        if auto_punch and chat_mode != "Normal Chat 💬":
            st.markdown('<div class="flash"></div>', unsafe_allow_html=True)

        if voice_enabled:
            lang_code = "ta" if language != "English" else "en"
            tts = gTTS(text=reply, lang=lang_code)
            filename = f"{uuid.uuid4()}.mp3"
            tts.save(filename)
            with open(filename, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
            os.remove(filename)

    st.session_state.messages.append({"role":"assistant","content":reply})
