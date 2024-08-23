import asyncio
import websockets
from config import load_config, print_neo4j_env_vars, test_dns_resolution, resolve_hostname
from database import Neo4jDatabase
from message_handler import MessageHandler

async def main():
    config = load_config()
    print_neo4j_env_vars()

    hostname = config["URI"].split("://")[1].split(":")[0] # e.g., "56efe15a.databases.neo4j.io"
    print(f"Hostname extracted for DNS resolution: {hostname}")
    test_dns_resolution(hostname)
    resolve_hostname(config["URI"])

    try:
        db = Neo4jDatabase(config["URI"], config["USER"], config["PASSWORD"])
        db.test_connection()

        handler = MessageHandler(db)
        
        server = await websockets.serve(
            handler.handle,
            "0.0.0.0",
            3001,
            process_request=lambda path, headers: None
        )
        print("WebSocket server started on ws://0.0.0.0:3001")
        await server.wait_closed()
    except Exception as e:
        print(f"Failed to start server: {e}")
        db.close()
        exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        db.close()