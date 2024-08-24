"""
This file appears to be a Python script that interacts with a Neo4j graph database to query and display instructions and their connections. It sets up the necessary environment variables for connecting to the Neo4j database, performs a query to retrieve instructions and their relationships, and then prints out the results. Additionally, there are commented-out sections that suggest potential visualization of the graph data using pyvis network. Overall, the purpose of this script seems to be querying and displaying graph data related to instructions in the context of DharmaBot UI.
"""

import os
from dotenv import load_dotenv
from pyvis.network import Network
from langchain_community.graphs import Neo4jGraph

load_dotenv()


os.environ["NEO4J_URI"] = os.getenv("neo4j_url")
os.environ["NEO4J_USERNAME"] = os.getenv("neo4j_username")
os.environ["NEO4J_PASSWORD"] = os.getenv("neo4j_pw")

# Import movie information

# load_data_query = """
# MERGE (intro:Instruction {description: "How to deal with first time users"})
# MERGE (firstTimeName:Name {value: "intro"})
# MERGE (intro)-[:HAS_NAME]->(firstTimeName)
# MERGE (firstTimeCondition:Condition {value: "is_first_time_user"})
# MERGE (intro)-[:HAS_CONDITION]->(firstTimeCondition)
# SET intro.content = "Greet the first time user to the Dharmaverse!"

# MERGE (characterCreation:Instruction {description: "Guide users through character creation"})
# MERGE (characterCreationName:Name {value: "character_creation"})
# MERGE (characterCreation)-[:HAS_NAME]->(characterCreationName)

# MERGE (worldExploration:Instruction {description: "Explain the Dharmaverse world to users"})
# MERGE (worldExplorationName:Name {value: "world_exploration"})
# MERGE (worldExploration)-[:HAS_NAME]->(worldExplorationName)

# MERGE (gameplayTutorial:Instruction {description: "Teach users how to play DharmaRPG"})
# MERGE (gameplayTutorialName:Name {value: "gameplay_tutorial"})
# MERGE (gameplayTutorial)-[:HAS_NAME]->(gameplayTutorialName)
# """
graph = Neo4jGraph()

query_data = '''
MATCH (i:Instruction)
OPTIONAL MATCH (i)-[r]->(connected)
RETURN i, collect({relationship: type(r), node: connected}) as connections
'''
result = graph.query(query_data)
# Display the result
print("Query Result:")
for record in result:
    instruction = record["i"]
    connections = record["connections"]
    
    print(f"\nInstruction: {instruction.get('description', 'N/A')}")
    print(f"Properties: {dict(instruction)}")
    
    if connections:
        print("Connections:")
        for connection in connections:
            connected_node = connection["node"]
            relationship = connection["relationship"]
            print(f"  - {relationship} -> {connected_node.get('value', 'N/A')} ({dict(connected_node)})")
    else:
        print("No connections")

# net = Network(notebook=True, cdn_resources='in_line')
           
# Add nodes and edges to the network
# for record in result:
#     instruction = record["i"]
#     connections = record["connections"]
    
#     # Add instruction node if 'id' and 'description' keys exist
#     if "id" in instruction and "description" in instruction:
#         print(f"Adding instruction node: {instruction['id']} - {instruction['description']}")
#         net.add_node(instruction["id"], label=instruction["description"])
    
#     # Add connected nodes and edges
#     for connection in connections:
#         connected_node = connection["node"]
#         relationship = connection["relationship"]
        
#         if connected_node and "id" in connected_node and "value" in connected_node:
#             print(f"Adding connected node: {connected_node['id']} - {connected_node['value']}")
#             net.add_node(connected_node["id"], label=connected_node["value"])
#             if "id" in instruction:
#                 print(f"Adding edge from {instruction['id']} to {connected_node['id']} with relationship {relationship}")
#                 net.add_edge(instruction["id"], connected_node["id"], title=relationship)

# # Save and display the network
# net.show("graph.html")
exit()

graph.refresh_schema()
print(graph.schema)

graph.query(movies_query)