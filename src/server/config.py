"""
This file contains functions related to loading configuration variables, printing Neo4j environment variables, testing DNS resolution, and resolving hostnames to IP addresses using sockets in Python. These functions aim to handle configurations, environment variables, and network-related tasks, which could be utilized in the DharmaBot UI for setting up connections to Neo4j databases, resolving hostnames, and managing API keys.
"""

import os
from dotenv import load_dotenv, find_dotenv
import socket

def load_config():
    dotenv_path = find_dotenv()
    if not dotenv_path:
        print("No .env file found")
    else:
        print(f"Loading .env file from: {dotenv_path}")
        load_dotenv(dotenv_path)

    return {
        "URI": os.getenv("neo4j_url"),
        "USER": os.getenv("neo4j_username"),
        "PASSWORD": os.getenv("neo4j_pw"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }

def print_neo4j_env_vars():
    for key, value in os.environ.items():
        if 'neo4j' in key.lower():
            print(f"{key}: {value}")

def test_dns_resolution(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"Successfully resolved {hostname} to {ip_address}")
    except socket.gaierror as e:
        print(f"Failed to resolve {hostname}: {e}")

def resolve_hostname(url):
    hostname = url.split("://")[1].split(":")[0]
    try:
        ip = socket.gethostbyname(hostname)
        print(f"Resolved {hostname} to {ip}")
    except socket.gaierror as e:
        print(f"Failed to resolve {hostname}: {e}")