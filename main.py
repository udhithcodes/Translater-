import os
import subprocess
import tempfile
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from gtts import gTTS

# ── Translation ──────────────────────────────────────────────────────────────

def translate_to_tamil(text: str) -> str:
    """Translate English → Tamil using Google's internal API (no key, no 429)."""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "en", "tl": "ta", "dt": "t", "q": text}
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return "".join(seg[0] for seg in data[0] if seg and seg[0])

# ── Voice Input ───────────────────────────────────────────────────────────────

def listen() -> str:
    """Record from mic and return recognised English text."""
    SAMPLE_RATE = 16000
    DURATION    = 5          # seconds to record

    print("🎤 Listening... (speak now)")
    audio_data = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    print("✅ Done recording.")

    # Save to a temp WAV file so SpeechRecognition can read it
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    wav.write(tmp_path, SAMPLE_RATE, audio_data)

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio = recognizer.record(source)
    os.remove(tmp_path)

    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio. Please try again.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return ""

# ── Voice Output ──────────────────────────────────────────────────────────────

def speak_tamil(text: str):
    """Convert Tamil text to speech and play it using macOS afplay."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        tts = gTTS(text=text, lang="ta")
        tts.save(tmp_path)
        subprocess.run(["afplay", tmp_path], check=True)
    finally:
        os.remove(tmp_path)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  🗣️  English → Tamil Voice Translator")
    print("  Type 'v' for voice input, or just type text.")
    print("  Type 'exit' to quit.")
    print("=" * 50)

    while True:
        mode = input("\n[v = voice / or type text]: ").strip()

        if mode.lower() == "exit":
            print("Goodbye! / போய் வருகிறேன்!")
            break

        if mode.lower() == "v":
            english_text = listen()
        else:
            english_text = mode

        if not english_text:
            continue

        print("⏳ Translating...")
        try:
            tamil_text = translate_to_tamil(english_text)
            print(f"🔤 Tamil: {tamil_text}")
            print("🔊 Speaking...")
            speak_tamil(tamil_text)
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()