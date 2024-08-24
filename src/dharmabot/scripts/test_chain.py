"""
This file is focused on setting up connections to various APIs and resources required for DharmaBot UI functionality. It initializes OpenAI and Neo4j connections, loads environment variables, creates prompts for interacting with the APIs, generates Cypher queries based on user instructions, and executes those queries on a Neo4j graph database. Additionally, it includes functionality for interacting with language models for generating responses based on prompts given to the system.
"""

from dharmabot.utils import flatten_list
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from neo4j import GraphDatabase, basic_auth
from prettytable import PrettyTable
from dotenv import load_dotenv
import os
load_dotenv()
from langchain_groq import ChatGroq 
from langchain_openai import ChatOpenAI 
import time
from langchain_community.graphs import Neo4jGraph


os.environ["NEO4J_URI"] = os.getenv("neo4j_url")
os.environ["NEO4J_USERNAME"] = os.getenv("neo4j_username")
os.environ["NEO4J_PASSWORD"] = os.getenv("neo4j_pw")



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

# messages = [
#     (
#         "system",
#         "You are a helpful translator. Translate the user sentence to French.",
#     ),
#     ("human", "I love programming."),
# ]

graph = Neo4jGraph()

system_arr = [
    "You are a Neo4j Cypher expert.", 
    "Your job is to write a Cypher query based on the given schema: \n {schema} \n and user instruction.",
    "Only output the cypher query. No text.",
    "Consider the following guidelines:",
    [
        "Use appropriate Cypher clauses (MATCH, WHERE, CREATE, SET, etc.) based on the user's request.",
        "Ensure proper node labels and relationship types are used as per the schema.",
        "Include any necessary properties or constraints mentioned in the user's request.",
        "Use parameters for dynamic values to prevent injection attacks.",
        "Optimize the query for performance when possible.",
    ],
    "If the user's request is unclear or lacks necessary information, ask for clarification before writing the query.",
]

system_prompt_text = flatten_list(system_arr)

prompt = ChatPromptTemplate.from_messages([
  ("system", system_prompt_text),
  ("human", "{text}")
])


# Create a test instruction for adding a new instruction node
express_query = "Create a new instruction node with the name 'daily_quest' and description 'Provide users with daily quests to complete in the Dharmaverse'"

# Chain the prompt with the LLM
chain = prompt | llm_groq

# Invoke the chain with the test instruction
cypher_query = chain.invoke({"text": express_query, "schema": graph.schema})

# Remove Markdown code block delimiters if present
cleaned_cypher_query = cypher_query.content.strip('```cypher').strip('```').strip()

print("Generated Cypher Query:")
print(cleaned_cypher_query)

# Execute the generated Cypher query
result = graph.query(cleaned_cypher_query)

print("\nQuery Execution Result:")
print(result)

exit()

start_time = time.time()
# result = llm_open_ai.invoke(messages)
graph.refresh_schema()
# print(graph.schema)
result = llm_groq.invoke(prompt.format(text="add a new instruction .", schema=graph.schema))
end_time = time.time()

response_time = end_time - start_time

print("Result:", result.content)
print("Meta:", result.response_metadata)
print(f"Response time: {response_time:.2f} seconds")

# response = 

# print(f"Prompt: {prompt}")
# print(f"Response: {response}")

exit()

msg_to_cypher_prompt = PromptTemplate(
    input_variables=["concept"],
    template="Explain the concept of {concept} in the context of the Dharmaverse."
)


# open_ai_llm = OpenAI(temperature=0.7)

system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | open_ai_llm


result = chain.invoke({"text": "Explain the importance of low latency LLMs."})






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