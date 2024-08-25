"""
This file contains a function `groq_basic` that formats a conversation for the Groq language model and generates a response. It allows for routing conversations to different agents and processing messages in various ways.
"""

from langchain.schema import HumanMessage, SystemMessage

def groq_basic(conversation, system_message, llm_openai, llm_groq):
    # Convert conversation to a format suitable for the LLM
    messages = [system_message]  # This is already a SystemMessage object
    for msg in conversation:
        role = "assistant" if msg["sender_type"] == "Agent" else "user"
        messages.append(HumanMessage(content=msg["content"]) if role == "user" else SystemMessage(content=msg["content"]))
    
    print("Debug: Formatted messages for LLM:")
    for msg in messages:
        print(f"  Role: {msg.__class__.__name__}, Content: {msg.content[:50]}...")
    
    # Choose which LLM to use (you can implement logic to switch between them)
    llm = llm_groq  # or llm_openai
    print(f"Debug: Using LLM: {type(llm).__name__}")
    
    try:
        response = llm.invoke(messages)
        print(f"Debug: LLM response received. Length: {len(response.content)}")
        return response.content
    except Exception as e:
        print(f"Debug: Error invoking LLM: {str(e)}")
        raise