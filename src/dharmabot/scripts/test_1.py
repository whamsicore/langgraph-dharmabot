"""
This file appears to serve as a script for interacting with various components of the DharmaBot UI system. It includes sections for utilizing OpenAI models, executing Groq queries, interacting with Neo4j graph database, and creating prompts for generating responses. The script demonstrates the functionality of translating text, generating responses, and querying a Neo4j database, showcasing the capabilities of DharmaBot UI in handling different types of interactions.
"""

from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from neo4j import GraphDatabase, basic_auth
from prettytable import PrettyTable
from dotenv import load_dotenv
import os
load_dotenv()
from langchain_groq import ChatGroq 
from langchain_openai import ChatOpenAI 

llm_open_ai = ChatOpenAI(
  model="gpt-4o",
  temperature=0,
  max_tokens=None,
  timeout=None,
  max_retries=2,
  api_key=os.getenv("OPENAI_API_KEY"),
  # base_url="...",
  # organization="...",
  # other params...
)

llm_groq = ChatGroq(
  model_name="llama-3.1-70b-versatile", 
  temperature=0, 
  max_tokens=None,
  groq_api_key=os.getenv("groq_api_key"),
  timeout=None,
  max_retries=2,
  )

messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
]
import time

start_time = time.time()
# result = llm_open_ai.invoke(messages)
result = llm_groq.invoke(messages)
end_time = time.time()

response_time = end_time - start_time

print("Result:", result.content)
print("Meta:", result.response_metadata)
print(f"Response time: {response_time:.2f} seconds")

exit()
# open_ai_llm = OpenAI(temperature=0.7)

system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | open_ai_llm


result = chain.invoke({"text": "Explain the importance of low latency LLMs."})

# End the script
# Prettify and print the results
print("\n--- Script Execution Results ---")
print(f"Prompt: {result}")
print("\nResponse:")
# print(result.content)
print("\nScript execution completed.")
print("--------------------------------")
exit()

# Access the API key from environment variables



# Create a test prompt
test_prompt = PromptTemplate(
    input_variables=["concept"],
    template="Explain the concept of {concept} in the context of the Dharmaverse."
)

# Example usage of the prompt
concept = "cybernetics"
prompt = test_prompt.format(concept=concept)
response = llm(prompt)

print(f"Prompt: {prompt}")
print(f"Response: {response}")

# Neo4j connection (replace with your actual credentials)
uri = "neo4j+s://86e1edfa.databases.neo4j.io"
user = "neo4j"
password = "DmQZDQy5MVe1O5zv_Ybp-4RQuXj4vbI6WByjHC7mXUE"

# Example Neo4j query with formatted output
try:
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    with driver.session() as session:
        result = session.run("MATCH (n:Character) RETURN n.name AS name LIMIT 5")
        
        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = ["Name"]
        
        for record in result:
            table.add_row([record["name"]])
        
        print(table)
    driver.close()
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")