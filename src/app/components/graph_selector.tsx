// This component renders a set of bubbles for selecting different graph types.

import React from 'react';

interface GraphSelectorProps {
  graph_types: string[];
  selected_graph: string;
  on_select_graph: (graph: string) => void;
}

const GraphSelector: React.FC<GraphSelectorProps> = ({ graph_types, selected_graph, on_select_graph }) => {
  return (
    <div className="flex justify-center space-x-4 p-4">
      {graph_types.map((graph_type) => (
        <button
          key={graph_type}
          className={`rounded-full px-4 py-2 text-sm font-medium ${
            selected_graph === graph_type
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => on_select_graph(graph_type)}
        >
          {graph_type}
        </button>
      ))}
    </div>
  );
};

export default GraphSelector;