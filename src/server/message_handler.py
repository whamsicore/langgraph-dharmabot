"""
This file contains a Python class `MessageHandler` that handles messages for a chatbot powered by two different language models (LLMs). It interacts with a database to store and retrieve messages, generates AI responses based on the conversation history, and sends those responses back to the user. The purpose of this file is to manage communication between users and the AI assistant, utilizing both OpenAI and Groq language models to generate responses.
"""

import json
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import asyncio
import traceback
from server.agents.groq_basic import groq_basic 

load_dotenv()

class MessageHandler:
    def __init__(self, database):
        self.database = database
        self.connected = set()
        self.llm_openai = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.llm_groq = ChatGroq(
            model_name="llama-3.1-70b-versatile", 
            temperature=0.7, 
            max_tokens=None,
            groq_api_key=os.getenv("groq_api_key"),
            timeout=None,
            max_retries=2,
        )
        self.system_message = SystemMessage(content="You are a helpful AI assistant.")
        self.message_lock = asyncio.Lock()

    async def handle(self, websocket, path):
        self.connected.add(websocket)
        try:
            chat_history = self.database.get_messages()
            await websocket.send(json.dumps({"type": "chat", "messages": chat_history}))
            
            async for websocket_message in websocket:
                data = json.loads(websocket_message)
                if data["type"] == "chat":
                    async with self.message_lock:
                        user_message = self.database.add_message(data["content"], data["sender_type"])
                        
                        try:
                            ai_response = self.generate_ai_response(chat_history + [user_message])
                            ai_message = self.database.add_message(ai_response, "Agent")
                            
                            await websocket.send(json.dumps({"type": "chat", "message": ai_message}))
                        except Exception as e:
                            print(f"Error generating AI response: {e}")
                            error_message = self.database.add_message("Sorry, I encountered an error while processing your request.", "Agent")
                            await websocket.send(json.dumps({"type": "chat", "message": error_message}))
        finally:
            self.connected.remove(websocket)

    async def handle_message(self, content, sender_type):
        print(f"Handling message: content='{content}', sender_type='{sender_type}'")
        async with self.message_lock:
            try:
                user_message = self.database.add_message(content, sender_type)
                print(f"User message added: {user_message}")
                
                chat_history = self.database.get_messages()
                print(f"Chat history retrieved, length: {len(chat_history)}")
                
                ai_response = self.generate_ai_response(chat_history)
                print(f"AI response generated: '{ai_response[:50]}...'")
                
                ai_message = self.database.add_message(ai_response, "Agent")
                print(f"AI message added: {ai_message}")
                
                return ai_message
            except Exception as e:
                print(f"Error in handle_message: {e}")
                print(traceback.format_exc())
                error_message = self.database.add_message("Sorry, I encountered an error while processing your request.", "Agent")
                return error_message

    def generate_ai_response(self, conversation):
        return groq_basic(conversation, self.system_message, self.llm_openai, self.llm_groq)  # Updated call

__all__ = ['MessageHandler']