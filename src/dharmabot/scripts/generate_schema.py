"""
This Python script serves the purpose of connecting to a Neo4j database, running specific Cypher queries to gather information about node labels, relationship types, and node properties, and then generating a markdown file that summarizes the schema of the Neo4j database. This script automates the process of documenting the database schema in a human-readable format for easier understanding and reference, which aligns with DharmaBot UI's goal of interacting with Neo4j databases and visualizing graph data.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Função para executar a consulta Cypher e retornar o resultado
def run_query(driver, query):
    with driver.session() as session:
        result = session.run(query)
        return [record for record in result]

# Função principal para gerar o esquema
def generate_schema():
    # Conecta ao banco de dados Neo4j
    uri = os.getenv("neo4j_url")
    user = os.getenv("neo4j_username")
    password = os.getenv("neo4j_pw")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        # Consulta para obter os rótulos dos nós
        node_labels_query = "CALL db.labels()"
        node_labels = run_query(driver, node_labels_query)

        # Consulta para obter os tipos de relacionamentos
        rel_types_query = "CALL db.relationshipTypes()"
        rel_types = run_query(driver, rel_types_query)

        # Consulta para obter as propriedades dos nós
        node_properties_query = """
        CALL db.schema.nodeTypeProperties()
        YIELD nodeLabels, propertyName, propertyTypes
        RETURN nodeLabels, collect({name: propertyName, types: propertyTypes}) as properties
        """
        node_properties = run_query(driver, node_properties_query)

        # Gera o conteúdo do arquivo markdown
        markdown_content = "# Esquema do Banco de Dados Neo4j\n\n"
        
        markdown_content += "## Rótulos de Nós\n\n"
        for label in node_labels:
            markdown_content += f"- {label['label']}\n"
        
        markdown_content += "\n## Tipos de Relacionamentos\n\n"
        for rel_type in rel_types:
            markdown_content += f"- {rel_type['relationshipType']}\n"
        
        markdown_content += "\n## Propriedades dos Nós\n\n"
        for node_type in node_properties:
            labels = ", ".join(node_type['nodeLabels'])
            markdown_content += f"### {labels}\n\n"
            for prop in node_type['properties']:
                prop_types = ", ".join(prop['types'])
                markdown_content += f"- {prop['name']}: {prop_types}\n"
            markdown_content += "\n"

        # Cria o diretório outputs se não existir
        os.makedirs("outputs", exist_ok=True)

        # Escreve o conteúdo no arquivo schema.md
        with open("outputs/schema.md", "w") as f:
            f.write(markdown_content)

        print("Esquema gerado com sucesso em outputs/schema.md")

    finally:
        driver.close()

if __name__ == "__main__":
    generate_schema()