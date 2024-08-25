"""
This script processes user input by retrieving the Perceptron and its associated filters from a Neo4j database, 
and then uses a language model to evaluate the filters based on the conversation context.
"""

import os
from neo4j import GraphDatabase
from langchain.schema import HumanMessage, SystemMessage
import asyncio

# Function to connect to Neo4j and retrieve filters
def retrieve_filters(driver):
    query = """
    MATCH (p:Perceptron)-[:HAS_FILTER]->(f:Filter)
    RETURN f.question AS question
    """
    with driver.session() as session:
        result = session.run(query)
        return [record["question"] for record in result]

async def process_filters(conversation, llm_groq):
    # Connect to the Neo4j database
    uri = os.getenv("neo4j_url")
    user = os.getenv("neo4j_username")
    password = os.getenv("neo4j_pw")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        # Retrieve filters from the database
        filter_questions = retrieve_filters(driver)
        
        # Convert conversation to a format suitable for the LLM
        messages = [SystemMessage(content="Process the following conversation:")]
        for msg in conversation:
            role = "assistant" if msg["sender_type"] == "Agent" else "user"
            messages.append(HumanMessage(content=msg["content"]) if role == "user" else SystemMessage(content=msg["content"]))
        
        print("Debug: Formatted messages for LLM:")
        for msg in messages:
            print(f"  Role: {msg.__class__.__name__}, Content: {msg.content[:50]}...")
        
        # Asynchronously process each filter question
        async_responses = []
        for question in filter_questions:
            prompt = f"{question} based on the conversation."
            async_responses.append(llm_groq.invoke_async([prompt]))  # Assuming llm_groq supports async
        
        # Collect responses
        responses = await asyncio.gather(*async_responses)
        
        # Output structured responses
        structured_responses = {}
        for question, response in zip(filter_questions, responses):
            structured_responses[question] = {
                "is_true": response.is_true,  # Assuming response has an is_true attribute
                "context": response.context if response.is_true else None
            }
        
        return structured_responses

    except Exception as e:
        print(f"Debug: Error in processing filters: {str(e)}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    # Example usage
    conversation = [{"sender_type": "User", "content": "What can you tell me about the agent?"}]
    llm_groq = ...  # Initialize your LLM here
    asyncio.run(process_filters(conversation, llm_groq))