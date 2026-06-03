import cohere
from rich import print
from dotenv import dotenv_values

env_var = dotenv_values(".env")

CohereAPIKey = env_var.get("CohereAPIKey")

co = cohere.Client(api_key=CohereAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write an application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model.
-> Respond with 'realtime ( query )' if a query requires up-to-date info.
-> Respond with 'open (application name)'
-> Respond with 'close (application name)'
-> Respond with 'play (song name)'
-> Respond with 'generate image (prompt)'
-> Respond with 'reminder (datetime with message)'
-> Respond with 'system (task name)'
-> Respond with 'content (topic)'
-> Respond with 'google search (topic)'
-> Respond with 'youtube search (topic)'
*** If multiple tasks: respond separately ***
*** goodbye → respond with 'exit' ***
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "content": f"{prompt}"})

    # ✅ FIX: Replace removed model with new working one
    stream = co.chat_stream(
        model="command-r-08-2024",   # ✅ THIS WILL NOT GIVE 404
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    response = ""

    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    response = response.replace("\n", "")
    response = response.split(",")
    response = [i.strip() for i in response]

    temp = []

    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)

    # ✅ Your original logic preserved
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return temp


if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))
