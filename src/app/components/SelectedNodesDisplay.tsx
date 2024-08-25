// This component displays the currently selected nodes from the context.

import React from 'react';
import { useNodeSelection } from '../context/node_selection_context'; // Import the context

const SelectedNodesDisplay: React.FC = () => {
  const { selected_nodes } = useNodeSelection(); // Use the context

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg w-full">
      <h2 className="text-lg font-bold">Selected Nodes</h2>
      {selected_nodes.length === 0 ? (
        <p>No nodes selected.</p>
      ) : (
        <div className="flex flex-wrap gap-2 mt-2">
          {selected_nodes.map(({ id, label }) => (
            <div key={id} className="bg-blue-600 rounded-full px-4 py-2 flex items-center">
              <span className="mr-2">{label}</span> {/* Display the node label */}
              {/* <span className="text-sm">{id}</span> Display the node ID */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SelectedNodesDisplay;