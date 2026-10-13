import time
from deep_translator import MyMemoryTranslator

print("Translator is running. Type 'exit' to quit.")

while True:
    text = input("\nEnter English text: ")
    
    if text.lower() == 'exit':
        break
        
    try:
        # Added a small delay to respect API rate limits
        time.sleep(1)
        translated = MyMemoryTranslator(source='en-US', target='ta-IN').translate(text)
        
        if translated:
            print("Tamil Translation:", translated)
        else:
            print("Translation failed: Received empty response from server.")
            
    except Exception as e:
        print("Translation failed:", e)