import requests

def translate_to_tamil(text: str) -> str:
    """
    Translates English text to Tamil using Google's internal API.
    No API key needed. Not subject to the 429 rate-limit that hits the scraper.
    """
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ta",
        "dt": "t",
        "q": text,
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    # data[0] is a list of [translated_chunk, original_chunk, ...]
    return "".join(segment[0] for segment in data[0] if segment and segment[0])

print("Google Translator (EN → Tamil). Type 'exit' to quit.")

while True:
    text = input("\nEnter English text: ").strip()

    if not text:
        continue

    if text.lower() == "exit":
        print("Goodbye!")
        break

    try:
        translation = translate_to_tamil(text)
        print("Tamil Translation:", translation)
    except requests.exceptions.RequestException as e:
        print("Network error:", e)
    except Exception as e:
        print("Translation failed:", e)