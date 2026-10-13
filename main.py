from deep_translator import GoogleTranslator

text = input("Enter English text: ")

translation = GoogleTranslator(source="en", target="ta").translate(text)

print("Tamil Translation:", translation)