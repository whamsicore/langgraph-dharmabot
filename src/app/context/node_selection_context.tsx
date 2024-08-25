// This context manages the state of selected nodes across the application.

import React, { createContext, useContext, useState } from 'react';

interface SelectedNode {
  id: string;
  label: string;
}

interface NodeSelectionContextType {
  selected_nodes: SelectedNode[];
  toggle_node_selection: (node: SelectedNode) => void;
  clear_all_selections: () => void;
}

const NodeSelectionContext = createContext<NodeSelectionContextType | undefined>(undefined);

export const NodeSelectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selected_nodes, set_selected_nodes] = useState<SelectedNode[]>([]);

  const toggle_node_selection = (node: SelectedNode) => {
    console.log(`Toggling selection for node: ${node.id} (${node.label})`);
    set_selected_nodes((prev) => {
      const exists = prev.find((n) => n.id === node.id);
      if (exists) {
        return prev.filter((n) => n.id !== node.id); // Remove node if already selected
      } else {
        return [...prev, node]; // Add node if not already selected
      }
    });
  };

  const clear_all_selections = () => {
    set_selected_nodes([]);
  };

  return (
    <NodeSelectionContext.Provider value={{ selected_nodes, toggle_node_selection, clear_all_selections }}>
      {children}
    </NodeSelectionContext.Provider>
  );
};

export const useNodeSelection = () => {
  const context = useContext(NodeSelectionContext);
  if (!context) {
    throw new Error('useNodeSelection must be used within a NodeSelectionProvider');
  }
  return context;
};