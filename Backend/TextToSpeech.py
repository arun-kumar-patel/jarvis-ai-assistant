import pyttsx3
import random
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

def get_tts_responses():
    """
    Returns a list of predefined responses for long text.
    """
    return [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

def TextToSpeech(text):
    """
    Given text, this function speaks it out using pyttsx3.
    Re-initializes engine each time to avoid hanging after the first run.
    Handles long text gracefully with predefined responses.
    """
    if not text:
        return "No text to speak."

    try:
        # Initialize engine fresh each time
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')

        # Set voice
        if AssistantVoice and any(v.id == AssistantVoice for v in voices):
            engine.setProperty('voice', AssistantVoice)
        else:
            engine.setProperty('voice', voices[0].id)

        # Set rate
        engine.setProperty('rate', 170)

        # Logic to handle long text
        sentences = str(text).split(".")
        if len(sentences) > 4 and len(text) >= 250:
            short_text = ".".join(sentences[:2]) + "."
            response_text = random.choice(get_tts_responses())

            # Speak short part
            engine.say(short_text)
            engine.runAndWait()

            # Speak predefined response
            engine.say(response_text)
            engine.runAndWait()
        else:
            # Speak full text
            engine.say(text)
            engine.runAndWait()

        engine.stop()  # Cleanup
        return "Success"

    except Exception as e:
        print(f"An error occurred while trying to speak: {e}")
        return "Failed"

# Main execution loop for testing
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        TextToSpeech(user_input)
