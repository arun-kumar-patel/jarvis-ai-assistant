import speech_recognition as sr
import mtranslate as mt
from dotenv import dotenv_values
import os
import pyaudio
import wave

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguages = env_vars.get("InputLanguage")

# Configuration for PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "audio.wav"

# Function for Query modification (to add punctuation and format)
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word in new_query.split() for word in question_words):
        if new_query.endswith(('.', '?', '!')):
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if not new_query.endswith(('.', '?', '!')):
            new_query += "."
    
    return new_query.capitalize()

# Function for text translation (if input is not in English)
def UniversalTranslator(Text):
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return Text

# Function for Speech-to-Text recognition using a more reliable method
def SpeechToText():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Stopped listening.")
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio_data = recognizer.record(source)
        
        # You can choose a better recognition service here. 
        # For this example, we'll continue with Google but with better error handling.
        recognized_text = recognizer.recognize_google(audio_data)
        os.remove(WAVE_OUTPUT_FILENAME)
        return recognized_text

    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        os.remove(WAVE_OUTPUT_FILENAME)
        return None
    except sr.RequestError as e:
        print(f"Sorry, could not request results from Google Speech Recognition service; {e}")
        os.remove(WAVE_OUTPUT_FILENAME)
        return None
    except FileNotFoundError:
        print("Audio file was not found, could not transcribe.")
        return None

# Function to process recognized text (including translation if required)
def ProcessText(Text):
    if Text:
        print(f"Recognized text: {Text}")
        processed_text = QueryModifier(Text)
        
        if InputLanguages.lower() != "en" and "en" not in InputLanguages.lower():
            translated_text = UniversalTranslator(Text)
            print(f"Translated to English: {translated_text}")
            return translated_text
        else:
            print("Text is in English. No translation needed.")
            return processed_text
    else:
        print("No text recognized.")
        return None

if __name__ == "__main__":
    while True:
        recognized_text = SpeechToText()
        if recognized_text:
            processed_query = ProcessText(recognized_text)
            if processed_query:
                print(f"Final processed query: {processed_query}")