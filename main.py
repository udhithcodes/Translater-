import os
import subprocess
import tempfile
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from gtts import gTTS

# ── Translation ──────────────────────────────────────────────────────────────

_GOOGLE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120"
}

def _google_translate(client: str, text: str) -> str:
    """Call Google's internal translate endpoint with a given client param."""
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": client, "sl": "en", "tl": "ta", "dt": "t", "q": text},
        headers=_GOOGLE_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    result = "".join(seg[0] for seg in data[0] if seg and seg[0])
    if not result:
        raise ValueError("Empty response")
    return result

def _mymemory_translate(text: str) -> str:
    """MyMemory free API — no key needed."""
    r = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": "en|ta"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    result = data["responseData"]["translatedText"]
    if not result or result.upper().startswith("QUERY LENGTH") or data.get("responseStatus") != 200:
        raise ValueError(f"MyMemory error: {result}")
    # Reject romanized responses (valid Tamil contains Tamil unicode chars)
    if result and not any('\u0B80' <= c <= '\u0BFF' for c in result):
        raise ValueError("Got romanized text, not Tamil script")
    return result

def translate_to_tamil(text: str) -> str:
    """Try 3 different free APIs in order until one works."""
    errors = []
    for strategy in [
        lambda: _google_translate("dict-chrome-ex", text),
        lambda: _google_translate("gtx", text),
        lambda: _mymemory_translate(text),
    ]:
        try:
            return strategy()
        except Exception as e:
            errors.append(str(e))
    raise RuntimeError(f"All translation APIs failed: {errors}")

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