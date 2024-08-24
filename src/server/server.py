"""
This Python script serves as the backend for the DharmaBot UI, handling WebSocket connections, sending chat history and graph data to clients, and updating the graph based on incoming messages. It also includes error handling and uses asyncio for asynchronous operations. The main purpose of this script is to establish and manage communication between the frontend interface and the Neo4j database, allowing users to interact with and visualize graph data in real-time.
"""

import asyncio
import websockets
from config import load_config, print_neo4j_env_vars, test_dns_resolution, resolve_hostname
from database import Neo4jDatabase
from message_handler import MessageHandler
from graph_handler import GraphHandler
import json
import traceback

async def handle_connection(websocket, path):
    print(f"New connection established: {websocket.remote_address}")
    try:
        # Send initial chat history
        chat_history = message_handler.database.get_messages()
        await websocket.send(json.dumps({"type": "chat", "messages": chat_history}))
        print("Initial chat history sent")

        # Send graph data
        print("Retrieving conversation graph...")
        graph_data = graph_handler.get_conversation_graph()
        print(f"Graph data retrieved: {json.dumps(graph_data, indent=2)}")
        await websocket.send(json.dumps({"type": "graph", "data": graph_data}))
        print("Graph data sent to client")

        # Keep the connection open and handle incoming messages
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30)
                print(f"Received message: {message}")
                data = json.loads(message)
                if data["type"] == "chat":
                    response = await message_handler.handle_message(data["content"], data["sender_type"])
                    await websocket.send(json.dumps({"type": "chat", "message": response}))
                    print("Chat response sent")
                    
                    # Send updated graph after each message
                    updated_graph_data = graph_handler.get_conversation_graph()
                    await websocket.send(json.dumps({"type": "graph", "data": updated_graph_data}))
                    print("Updated graph data sent")
            except asyncio.TimeoutError:
                print("No message received, sending ping")
                await websocket.ping()
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break
            except Exception as e:
                print(f"Error handling message: {e}")
                print(traceback.format_exc())
                await websocket.send(json.dumps({"type": "error", "message": str(e)}))
    except Exception as e:
        print(f"Error in handle_connection: {e}")
        print(traceback.format_exc())

async def main():
    config = load_config()
    print_neo4j_env_vars()

    hostname = config["URI"].split("://")[1].split(":")[0]
    print(f"Hostname extracted for DNS resolution: {hostname}")
    test_dns_resolution(hostname)
    resolve_hostname(config["URI"])

    try:
        db = Neo4jDatabase(config["URI"], config["USER"], config["PASSWORD"])
        db.test_connection()

        global message_handler, graph_handler
        message_handler = MessageHandler(db)
        graph_handler = GraphHandler(db)

        server = await websockets.serve(
            handle_connection,
            "0.0.0.0",
            3001,
            ping_interval=20,
            ping_timeout=60,
            process_request=lambda path, headers: None
        )
        print("WebSocket server started on ws://0.0.0.0:3001")
        await server.wait_closed()
    except Exception as e:
        print(f"Failed to start server: {e}")
        print(traceback.format_exc())
        db.close()
        exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        print(traceback.format_exc())
    finally:
        db.close()