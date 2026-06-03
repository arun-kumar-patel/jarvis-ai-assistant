# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import time

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes for passing specific elements in HTML content.
classes = [
    "zCubwf", "hgKElc", "LTK00 sY7ric", "Z0Lcw", "gsrt vk_bk FzvWSB YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6D LTKOO", "vlzY6d", "webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWKfKe", "VQF4g", "qv3Wpe", "Kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests.
useragent = (
    'Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/100.0.4896.75 Safari/537.36'
)

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority. Feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": "Hello, I am a content writer. You have to write content like a letter."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save it to a file.
def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        global messages
        messages = [{"role": "user", "content": f"{prompt}"}]

        try:
            # AI Response Generate
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stop=None
            )
            # AI Response Extract Properly
            Answer = completion.choices[0].message.content
            messages.append({"role": "assistant", "content": Answer})
            return Answer
        except Exception as e:
            return f"Error generating content: {e}"

    # Topic ko clean karna
    Topic = Topic.strip()
    ContentByAI = ContentWriterAI(f"Write about {Topic}")

    # File path set karna
    file_path = rf"Data\{Topic.lower().replace(' ', '_')}.txt"
    os.makedirs("Data", exist_ok=True)

    # File mein content write karna
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    # Notepad open karna
    OpenNotepad(file_path)
    return True

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query)
    return True

# Function to open an application.
def OpenApp(app_name):
    try:
        # Attempt to open the application using AppOpener
        appopen(app_name, match_closest=True, output=True, throw_error=True)
        print(f"Application '{app_name}' opened successfully.")
        return True
    except Exception as e:
        print(f"Error while opening application '{app_name}': {e}")
        
        # If AppOpener fails, try using subprocess to open the app
        try:
            subprocess.Popen([app_name])
            print(f"Application '{app_name}' opened successfully using subprocess.")
            return True
        except Exception as subprocess_error:
            print(f"Error while opening application '{app_name}' using subprocess: {subprocess_error}")
            return False


# Function to close an application.
def CloseApp(app):
    # If the app is Chrome, do nothing
    if "chrome" in app.lower():
        print("Skipping Chrome. It will not be closed.")
        return False
    else:
        try:
            # Try to close the app
            close(app, match_closest=True, output=True, throw_error=True)
            print(f"Application '{app}' closed successfully.")
            return True
        except Exception as e:
            # Handle any error that occurs
            print(f"Error while closing application '{app}': {e}")
            return False

# Function to execute system-level commands.
def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command[5:]))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command[6:]))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command[5:]))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command[8:]))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command[14:]))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command[15:]))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command[7:]))
        elif command.startswith("generate image"):
            # Image generation logic is now handled in Main.py, so we can pass
            # this command here without an error.
            pass
        else:
            print(f"No function found for: {command}")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Main function to automate command execution.
async def Automation(commands):
    async for result in TranslateAndExecute(commands):
        print(result)
    return True

if __name__ == "__main__":
    print("[yellow]Code execution started.[/yellow]")