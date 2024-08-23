from neo4j import GraphDatabase

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        """
        Initialize the Neo4jDatabase instance.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the connection to the Neo4j database.
        """
        self.driver.close()

    def test_connection(self):
        with self.driver.session(database="neo4j") as session:  # Specify the database
            result = session.run("RETURN 1 AS num")
            print("Successfully connected to Neo4j")

    def get_messages(self):
        """
        Retrieve all messages attached to the default conversation from the Neo4j database.
        """
        with self.driver.session(database="neo4j") as session:
            result = session.run("""
                MATCH (c:Conversation {id: 'default'})-[:HAS_MESSAGE]->(m:Message)<-[:SENT]-(sender)
                RETURN m.content AS content, m.timestamp AS timestamp,
                       labels(sender) AS sender_labels, sender.id AS sender_id
                ORDER BY m.timestamp
            """)
            return [
                {
                    "content": record["content"],
                    "timestamp": record["timestamp"].isoformat(),
                    "sender_type": record["sender_labels"][0],
                    "sender_id": record["sender_id"]
                }
                for record in result
            ]

    def add_message(self, content, sender_type):
        """
        Add a new message to the Neo4j database.
        """
        with self.driver.session(database="neo4j") as session:
            result = session.run("""
                MATCH (c:Conversation {id: 'default'})
                MATCH (sender:User {id: 'test_user'})
                WITH c, sender, CASE WHEN $sender_type = 'User' THEN sender ELSE null END as user_sender
                OPTIONAL MATCH (agent:Agent {id: 'test_agent'})
                WITH c, CASE WHEN $sender_type = 'User' THEN user_sender ELSE agent END as actual_sender
                CREATE (m:Message {id: randomUUID(), content: $content, timestamp: datetime()})
                CREATE (c)-[:HAS_MESSAGE]->(m)
                CREATE (actual_sender)-[:SENT]->(m)
                RETURN m
            """, content=content, sender_type=sender_type)
            
            message = result.single()['m']
            return {
                'id': message['id'],
                'content': message['content'],
                'timestamp': str(message['timestamp']),
                'sender_type': sender_type
            }