from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("neo4j_url")
user = os.getenv("neo4j_username")
password = os.getenv("neo4j_pw")

class DemoSetup:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_conversation(self):
        with self.driver.session(database="neo4j") as session:
            session.run("""
                MATCH (c:Conversation {id: 'default'})-[r:HAS_MESSAGE]->(m:Message)
                DETACH DELETE m
            """)

    def setup_demo(self):
        with self.driver.session(database="neo4j") as session:
            session.run("""
                MERGE (c:Conversation {id: 'default'})
                MERGE (u:User {id: 'test_user'})
                MERGE (a:Agent {id: 'test_agent'})
                
                WITH c, u, a
                
                CREATE (m1:Message {id: randomUUID(), content: 'Hello, Dharmabot!', timestamp: datetime()})
                CREATE (c)-[:HAS_MESSAGE]->(m1)
                CREATE (u)-[:SENT]->(m1)
                
                CREATE (m2:Message {id: randomUUID(), content: 'Hey there, player! How can I assist you today?', timestamp: datetime()})
                CREATE (c)-[:HAS_MESSAGE]->(m2)
                CREATE (a)-[:SENT]->(m2)
            """)

if __name__ == "__main__":
    demo_setup = DemoSetup(uri, user, password)
    demo_setup.clear_conversation()
    demo_setup.setup_demo()
    demo_setup.close()
    print("Demo conversation set up successfully.")