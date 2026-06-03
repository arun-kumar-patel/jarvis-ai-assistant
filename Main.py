import webbrowser
import subprocess
import threading
import json
import os
import sys  # FIXED: sys ko import kiya graceful exit ke liye
from time import sleep
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechToText
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

# FIXED: subprocess_list ko remove kar diya gaya hai kyunki yeh istemal nahi ho raha tha.
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "reminder", "generate image"]

def ShowDefaultChatIfNoChats():
    try:
        # Check if file is empty or just created
        if not os.path.exists(r'Data\ChatLog.json') or os.path.getsize(r'Data\ChatLog.json') < 5:
            with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
                file.write("")
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json file not found during default chat check.")
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            Chatlog_data = json.load(file)
            return Chatlog_data
    except FileNotFoundError:
        print("ChatLog.json file not found.")
        return []
    except json.JSONDecodeError:
        print("ChatLog.json is empty or invalid, returning empty list.")
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        # IMPROVED: String formatting ko direct aur clean kar diya hai
        if entry["role"] == "user":
            formatted_chatlog += f"{Username} : {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname} : {entry['content']}\n"
    
    # IMPROVED: Redundant .replace() calls ko hata diya gaya hai
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
            Data = File.read()
        
        if len(Data) > 0:
            # IMPROVED: Redundant .split() aur .join() ko hata diya
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(Data)
    except Exception as e:
        print(f"Error in ShowChatOnGUI: {e}")


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

def handle_tasks(decision_list):
    task_queries = [q for q in decision_list if any(q.startswith(func) for func in Functions)]
    if task_queries:
        print(f"Executing tasks: {task_queries}")
        run(Automation(task_queries))
        return True
    return False

def handle_image_generation(decision_list):
    image_query = next((q for q in decision_list if q.startswith("generate image")), None)
    if image_query:
        print(f"Starting ImageGeneration with query: {image_query}")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            # FIXED: .communicate() input ke sath istemal kiya gaya hai.
            # Yeh process ko query send karega, complete hone ka wait karega, aur output return karega.
            stdout, stderr = p1.communicate(input=f"{image_query}\n".encode())
            
            if stdout:
                print(f"ImageGeneration.py Output: {stdout.decode()}")
            if stderr:
                print(f"ImageGeneration.py Error: {stderr.decode()}")
            
            # FIXED: subprocess_list.append(p1) ko hata diya gaya hai.
            return True
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
    return False

def handle_conversational_queries(decision_list):
    general_queries = [q for q in decision_list if q.startswith("general")]
    realtime_queries = [q for q in decision_list if q.startswith("realtime")]

    query_to_process = ""
    is_realtime = False

    if general_queries and realtime_queries:
        # Dono ko merge kar do
        merged_query = " and ".join([" ".join(i.split()[1:]) for i in general_queries + realtime_queries])
        query_to_process = QueryModifier(merged_query)
        is_realtime = True
    elif general_queries:
        query_to_process = " ".join([" ".join(q.split()[1:]) for q in general_queries])
        query_to_process = QueryModifier(query_to_process)
    elif realtime_queries:
        query_to_process = " ".join([" ".join(q.split()[1:]) for q in realtime_queries])
        query_to_process = QueryModifier(query_to_process)
        is_realtime = True
    else:
        # Koi conversational query nahi hai
        return

    Answer = ""
    if is_realtime:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(query_to_process)
    else:
        SetAssistantStatus("Thinking...")
        Answer = ChatBot(query_to_process)

    ShowTextToScreen(f"{Assistantname} : {Answer}")
    SetAssistantStatus("Answering...")
    TextToSpeech(Answer)


def MainExecution():
    SetAssistantStatus("Listening...")
    Query = SpeechToText()

    if not Query or Query.strip() == "":
        SetAssistantStatus("Available...")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    
    try:
        Decision = FirstLayerDMM(Query)
        print(f"\nDecision: {Decision}\n")
    except Exception as e:
        print(f"Error in FirstLayerDMM: {e}")
        SetAssistantStatus("Available...")
        return

    if "exit" in Decision:
        SetAssistantStatus("Answering...")
        exit_message = "Okay, bye!"
        TextToSpeech(exit_message)
        ShowTextToScreen(f"{Assistantname} : {exit_message}")
        sleep(1)
        # FIXED: os._exit(1) ko sys.exit(0) se replace kiya
        # Yeh program ko gracefully exit karega.
        sys.exit(0)

    is_task_executed = handle_tasks(Decision)
    is_image_executed = handle_image_generation(Decision)

    if not is_task_executed and not is_image_executed:
        handle_conversational_queries(Decision)
        
    SetAssistantStatus("Available...")

def FirstThread():
    # Pehli baar run hone par setup
    InitialExecution()
    
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            if CurrentStatus == "True":
                MainExecution()
            else:
                # Jab mic off ho, toh CPU usage kam karne ke liye sleep
                sleep(0.1)
                AIStatus = GetAssistantStatus()
                if "Available..." not in AIStatus:
                    SetAssistantStatus("Available...")
                    
        except Exception as e:
            print(f"Error in FirstThread loop: {e}")
            SetAssistantStatus("Available...")
            sleep(1) # Error ke case mein thoda wait karo

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    # Logic thread ko daemon banaya taaki GUI band hone par yeh automatically band ho jaye
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    
    # GUI ko main thread par run kiya
    SecondThread()