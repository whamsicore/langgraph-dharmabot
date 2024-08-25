"""
This Python script connects to a Neo4j database and executes specific Cypher statements to create nodes and relationships representing a Perceptron and its associated Processing Filters. This script automates the process of populating the Neo4j database with initial data, which is essential for the functionality of the DharmaBot UI in processing user queries and interactions.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to execute a Cypher query
def run_query(driver, query):
    with driver.session() as session:
        try:
            session.run(query)
        except Exception as e:
            print(f"An error occurred: {e}")

# Main function to create the perceptron schema
def create_perceptron_schema():
    # Connect to the Neo4j database
    uri = os.getenv("neo4j_url")
    user = os.getenv("neo4j_username")
    password = os.getenv("neo4j_pw")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        # Cypher statements to create nodes and relationships
        cypher_statements = """
        MATCH (default_agent:Agent {id: 'test_agent'}) // Match the existing default agent node
        CREATE 
        (p:Perceptron {name: 'basic_perceptron'}),
        (f1:Filter {question: 'Is user is asking a question about the agent'}),
        (f2:Filter {question: 'Is user is telling us something about themself'}),
        (f3:Filter {question: 'Is User asking something about the real world?'}),
        (f4:Filter {question: 'Is user asking question about dharmaverse?'}),
        (f5:Filter {question: 'Is user asking to manipulate the Neo4j database?'}),
        (default_agent)-[:HAS_PERCEPTRON]->(p), // Attach perceptron to the existing default agent
        (p)-[:HAS_FILTER]->(f1),
        (p)-[:HAS_FILTER]->(f2),
        (p)-[:HAS_FILTER]->(f3),
        (p)-[:HAS_FILTER]->(f4),
        (p)-[:HAS_FILTER]->(f5);
        """
        run_query(driver, cypher_statements)

        print("Perceptron schema created successfully.")

    finally:
        driver.close()

if __name__ == "__main__":
    create_perceptron_schema()