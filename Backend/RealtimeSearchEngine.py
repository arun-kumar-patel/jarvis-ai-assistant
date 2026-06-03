from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""
Hello, I am {Username}. 
You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time information from the internet.

*** Provide answers professionally with proper grammar, punctuation, full stops, and clarity. ***
*** Only answer from the provided data in a clean and professional way. ***
"""

# ✅ Safe System Prompt
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# ✅ Load ChatLog
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    try:
        results = list(search(query, num_results=5))
    except:
        return "No valid search results found."

    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nLink: {i.url}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(text):
    lines = text.split('\n')
    clean = [line.strip() for line in lines if line.strip()]
    return "\n".join(clean)

def Information():
    now = datetime.datetime.now()
    return f"""
Use This Real-time Information if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H:%M:%S')}
"""

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # ✅ Reload chatlog fresh
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
    except:
        messages = []

    # ✅ Add only user message
    messages.append({"role": "user", "content": prompt})

    # ✅ Add temporary internet search info
    temp_system = {"role": "system", "content": GoogleSearch(prompt)}
    SystemChatBot.append(temp_system)

    # ✅ Streaming response
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        stream=True
    )

    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")

    # ✅ Save assistant reply
    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    # ✅ Remove temporary Google search info
    SystemChatBot.remove(temp_system)

    return AnswerModifier(Answer)


# ✅ Test Mode Only
if __name__ == "__main__":
    while True:
        prompt = input("Enter query: ")
        print(RealtimeSearchEngine(prompt))
