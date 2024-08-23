import json
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

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

    async def handle(self, websocket, path):
        self.connected.add(websocket)
        try:
            chat_history = self.database.get_messages()
            await websocket.send(json.dumps({"type": "chat", "messages": chat_history}))
            
            async for websocket_message in websocket:
                data = json.loads(websocket_message)
                if data["type"] == "chat":
                    user_message = self.database.add_message(data["content"], data["sender_type"])
                    
                    try:
                        ai_response = self.generate_ai_response(chat_history + [user_message])
                        ai_message = self.database.add_message(ai_response, "Agent")
                        
                        chat_history.extend([user_message, ai_message])
                        
                        for conn in self.connected:
                            await conn.send(json.dumps({"type": "chat", "message": ai_message}))
                    except Exception as e:
                        print(f"Error generating AI response: {e}")
                        error_message = self.database.add_message("Sorry, I encountered an error while processing your request.", "Agent")
                        await websocket.send(json.dumps({"type": "chat", "message": error_message}))
        finally:
            self.connected.remove(websocket)

    def generate_ai_response(self, conversation):
        # Convert conversation to a format suitable for the LLM
        messages = [self.system_message]  # This is already a SystemMessage object
        for msg in conversation:
            role = "assistant" if msg["sender_type"] == "Agent" else "user"
            messages.append(HumanMessage(content=msg["content"]) if role == "user" else SystemMessage(content=msg["content"]))
        
        print("Debug: Formatted messages for LLM:")
        for msg in messages:
            print(f"  Role: {msg.__class__.__name__}, Content: {msg.content[:50]}...")
        
        # Choose which LLM to use (you can implement logic to switch between them)
        llm = self.llm_groq  # or self.llm_openai
        print(f"Debug: Using LLM: {type(llm).__name__}")
        
        try:
            response = llm.invoke(messages)
            print(f"Debug: LLM response received. Length: {len(response.content)}")
            return response.content
        except Exception as e:
            print(f"Debug: Error invoking LLM: {str(e)}")
            raise

__all__ = ['MessageHandler']