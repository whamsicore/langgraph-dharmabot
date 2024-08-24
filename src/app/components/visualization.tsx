// This file now serves as a container for multiple graph visualizations and manages the selection between them.

'use client';

import { useState, useEffect, useRef } from 'react';
import GraphSelector from './graph_selector';
import ConversationGraph from './conversation_graph';
import KnowledgeGraph from './knowledge_graph';
import EntityGraph from './entity_graph';

const GRAPH_TYPES = ['Conversation', 'Knowledge', 'Entity'];
const WS_URL = 'ws://localhost:3001';

export default function Visualization() {
  const [selected_graph, set_selected_graph] = useState(GRAPH_TYPES[0]);
  const [graph_data, set_graph_data] = useState(null);
  const ws_ref = useRef(null);

  useEffect(() => {
    const connect_web_socket = () => {
      console.log(`Attempting to connect to WebSocket at ${WS_URL}`);
      const ws = new WebSocket(WS_URL);
      ws_ref.current = ws;

      ws.onopen = () => {
        console.log('Connected to WebSocket');
        ws.send(JSON.stringify({ type: 'get_graph_data', graph: selected_graph }));
      };

      ws.onmessage = (event) => {
        console.log('Received message:', event.data);
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'graph') {
            set_graph_data(data.data);
          } else {
            console.log('Received non-graph data:', data);
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason}`);
        setTimeout(connect_web_socket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connect_web_socket();

    return () => {
      if (ws_ref.current) {
        ws_ref.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (ws_ref.current && ws_ref.current.readyState === WebSocket.OPEN) {
      ws_ref.current.send(JSON.stringify({ type: 'get_graph_data', graph: selected_graph }));
    }
  }, [selected_graph]);

  const render_selected_graph = () => {
    switch (selected_graph) {
      case 'Conversation':
        return <ConversationGraph data={graph_data} />;
      case 'Knowledge':
        return <KnowledgeGraph data={graph_data} />;
      case 'Entity':
        return <EntityGraph data={graph_data} />;
      default:
        return null;
    }
  };

  return (
    <div className="w-full h-full bg-gray-900 flex flex-col">
      <GraphSelector
        graph_types={GRAPH_TYPES}
        selected_graph={selected_graph}
        on_select_graph={set_selected_graph}
      />
      <div className="flex-grow">
        {render_selected_graph()}
      </div>
    </div>
  );
}