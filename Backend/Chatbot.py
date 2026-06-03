from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# Global messages list
messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
except Exception as e:
    print(f"Error loading ChatLog.json: {e}")
    messages = []

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours :"
        f"{current_date_time.strftime('%M')} minutes :"
        f"{current_date_time.strftime('%S')} seconds.\n"
    )

def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

def ChatBot(Query):
    try:
        messages.append({"role": "user", "content": f"{Query}"})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ Updated model name
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error in ChatBot: {e}")
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        return "Sorry, an error occurred. Please check the console for details."