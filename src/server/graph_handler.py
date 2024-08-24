"""
This Python file defines a `GraphHandler` class that interacts with a Neo4j database to retrieve conversation data and represent it as nodes and links for a graph visualization. The purpose of this file is to handle the logic of querying the database for conversation-related information and formatting it into a graph structure that can be used by DharmaBot UI to display conversation graphs.
"""

from database import Neo4jDatabase

class GraphHandler:
    def __init__(self, db: Neo4jDatabase):
        self.db = db

    def get_conversation_graph(self, conversation_id: str = "default"):
        query = """
        MATCH (c:Conversation {id: $conversation_id})-[:HAS_MESSAGE]->(m:Message)<-[:SENT]-(sender)
        RETURN c, m, sender
        """
        result = self.db.run_query(query, {"conversation_id": conversation_id})

        nodes = []
        links = []
        node_ids = set()

        for record in result:
            conversation = record["c"]
            message = record["m"]
            sender = record["sender"]

            if conversation["id"] not in node_ids:
                nodes.append({
                    "id": conversation["id"],
                    "label": f"Conversation: {conversation['id']}",
                    "type": "conversation"
                })
                node_ids.add(conversation["id"])

            if message["id"] not in node_ids:
                nodes.append({
                    "id": message["id"],
                    "label": f"Message: {message['content'][:20]}...",
                    "type": "message"
                })
                node_ids.add(message["id"])

            if sender["id"] not in node_ids:
                nodes.append({
                    "id": sender["id"],
                    "label": f"{list(sender.labels)[0]}: {sender['id']}",
                    "type": list(sender.labels)[0].lower()
                })
                node_ids.add(sender["id"])

            links.append({
                "source": conversation["id"],
                "target": message["id"],
                "type": "HAS_MESSAGE"
            })
            links.append({
                "source": sender["id"],
                "target": message["id"],
                "type": "SENT"
            })

        return {
            "nodes": nodes,
            "links": links
        }