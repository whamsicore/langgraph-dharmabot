from typing import Literal

from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import AIMessage

from langgraph_engineer.check import check
from langgraph_engineer.critique import critique
from langgraph_engineer.draft import draft_answer
from langgraph_engineer.gather_requirements import gather_requirements
from langgraph_engineer.state import AgentState, OutputState, GraphConfig



def route_is_admin(state: AgentState) -> Literal["is_admin", "is_not_admin"]:
    if isinstance(state['isAdmin'][-1], AIMessage):
        return "critique"
    else:
        return "draft_answer"
from neo4j import GraphDatabase
from typing import Dict

def remember_user(state: AgentState, config: GraphConfig) -> AgentState:
    user_id = state.get('context', {}).get('user_id')
    if not user_id:
        return state

    # Connect to Neo4j
    driver = GraphDatabase.driver(
        config['neo4j_url'],
        auth=(config['neo4j_username'], config['neo4j_password'])
    )

    # Query the database
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User {id: $user_id}) "
            "OPTIONAL MATCH (u)-[:HAS_PREFERENCE]->(p:Preference) "
            "RETURN u, collect(p) as preferences",
            user_id=user_id
        )
        user_data = result.single()

    if user_data:
        user = user_data['u']
        preferences = user_data['preferences']
        
        # Update state with user information
        state['context']['user_info'] = {
            'name': user.get('name'),
            'email': user.get('email'),
            'preferences': [pref.get('name') for pref in preferences if pref]
        }

    driver.close()
    return state



def route_start(state: AgentState) -> Literal["draft_answer", "gather_requirements"]:
    if state.get('context').user:
        return "remember_user"
    else:
        return "perceive_message"
    
def route_check(state: AgentState) -> Literal["critique", "draft_answer"]:
    if isinstance(state['messages'][-1], AIMessage):
        return "critique"
    else:
        return "draft_answer"




def route_gather(state: AgentState) -> Literal["draft_answer", END]:
    if state.get('requirements'):
        return "draft_answer"
    else:
        return END

def route_critique(state: AgentState) -> Literal["draft_answer", END]:
    if state['accepted']:
        return END
    else:
        return "draft_answer"

def custom_node(state: AgentState, config: GraphConfig) -> AgentState:
    print("---Step 2---")
    pass
    

# Add the custom node to the dharmaflow

# Define a new graph
dharmaflow = StateGraph(AgentState, input=MessagesState, output=OutputState, config_schema=GraphConfig)
dharmaflow.set_conditional_entry_point(route_start)
dharmaflow.add_node(remember_user)
dharmaflow.add_edge("remember_user", "perceive_message")
dharmaflow.add_node("perceive_message")

dharmaflow.add_node(draft_answer)
dharmaflow.add_node(gather_requirements)
dharmaflow.add_node(critique)
dharmaflow.add_node(check)
dharmaflow.add_node("test_node", custom_node)
dharmaflow.add_conditional_edges("gather_requirements", route_gather)
dharmaflow.add_edge("draft_answer", "test_node")
dharmaflow.add_edge("test_node", "check")
dharmaflow.add_conditional_edges("check", route_check)
dharmaflow.add_conditional_edges("critique", route_critique)
graph = dharmaflow.compile()
