// This file contains a React component called Visualization, which is responsible for rendering and updating a graph visualization based on incoming data received through a WebSocket connection. The component uses D3.js for graph rendering and simulation, incorporating features like zooming, node dragging, and dynamic node styling based on node types. Additionally, it handles different types of data, such as graph data and chat messages, updating the visualization accordingly. This component serves as the core interface for displaying and interacting with graph data in the DharmaBot UI.

'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Node {
  id: string;
  label: string;
  type: string;
  content?: string;
}

interface Link {
  source: string;
  target: string;
  type: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function Visualization() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const socket = new WebSocket('ws://localhost:3001');

      socket.onopen = () => {
        console.log('WebSocket connected');
      };

      socket.onmessage = (event) => {
        console.log('WebSocket message received:', event);
        const data = JSON.parse(event.data);
        console.log('Parsed data:', data);
        if (data.type === 'graph') {
          console.log('Graph data received:', data.data);
          setGraphData(data.data);
        } else if (data.type === 'chat') {
          console.log('Chat data received:', data.messages || data.message);
          if (data.messages) {
            setChatMessages(data.messages);
          } else if (data.message) {
            setChatMessages(prevMessages => [...prevMessages, data.message]);
          }
        } else {
          console.log('Unknown data type received:', data);
        }
      };

      socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event);
        setTimeout(connectWebSocket, 5000); // Attempt to reconnect after 5 seconds
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      socketRef.current = socket;
    };

    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const width = svg.node()?.getBoundingClientRect().width || 800;
    const height = svg.node()?.getBoundingClientRect().height || 600;

    svg.selectAll("*").remove();

    const zoom_behavior = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom_behavior as any);

    const g = svg.append("g");

    const calculate_node_radius = (d: Node) => {
      const padding = 4; // Slightly increased padding
      const base_radius = d.type === "conversation" ? 12 : 8; // Slightly reduced base radius
      const text_width = d.type.length * 3; // Adjusted text width calculation
      return Math.max(base_radius, text_width / 2 + padding);
    };

    const simulation = d3.forceSimulation(graphData.nodes as d3.SimulationNodeDatum[])
      .force("link", d3.forceLink(graphData.links).id((d: any) => d.id).distance(100)) // Reduced distance
      .force("charge", d3.forceManyBody().strength(-300)) // Reduced repulsion
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => calculate_node_radius(d) + 1)); // Slightly reduced collision radius

    const link_group = g.append("g")
      .selectAll("g")
      .data(graphData.links)
      .join("g");

    link_group.append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6);

    link_group.append("text")
      .attr("font-size", "5px") // Reduced from 6px to 5px
      .attr("fill", "white") // Changed from black to white
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "text-after-edge")
      .text(d => d.type);

    const get_node_color = (d: Node) => {
      switch (d.type) {
        case "user": return "#0000FF";  // Blue
        case "agent": return "#FF0000";  // Red
        case "message": return "#87CEFA";  // Light Sky Blue
        case "conversation": return "#FFA500";  // Orange
        default: return "#808080";  // Gray for unknown types
      }
    };

    // Add a glow filter
    const defs = svg.append("defs");
    const filter = defs.append("filter")
      .attr("id", "glow");
    filter.append("feGaussianBlur")
      .attr("stdDeviation", "3")
      .attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode")
      .attr("in", "coloredBlur");
    feMerge.append("feMergeNode")
      .attr("in", "SourceGraphic");

    const node_group = g.append("g")
      .selectAll("g")
      .data(graphData.nodes)
      .join("g")
      .call(drag(simulation) as any);

    node_group.append("circle")
      .attr("r", calculate_node_radius)
      .attr("fill", get_node_color)
      .style("filter", "url(#glow)"); // Apply the glow effect

    node_group.append("text")
      .text((d) => d.type)
      .attr("font-size", (d) => `${Math.min(calculate_node_radius(d) * 0.8, 8)}px`) // Dynamic font size
      .attr("fill", "black") // Changed text color to black
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("dy", 0);

    node_group.append("title")
      .text((d) => {
        if (d.type === "message") {
          return `Message: ${d.label}\nContent: ${d.content || 'N/A'}`;
        } else if (d.type === "conversation") {
          return `Conversation: ${d.label}`;
        } else if (d.type === "user" || d.type === "agent") {
          return `${d.type.charAt(0).toUpperCase() + d.type.slice(1)}: ${d.label}`;
        } else {
          return `${d.type}: ${d.label}`;
        }
      });

    simulation.on("tick", () => {
      link_group.select("line")
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      link_group.select("text")
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);

      node_group
        .attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    function drag(simulation: d3.Simulation<d3.SimulationNodeDatum, undefined>) {
      function dragstarted(event: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event: any) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }

    simulation.alpha(0.5).restart(); // Reduced initial alpha for less aggressive start
  }, [graphData]);

  return (
    <div className="w-full h-full bg-gray-900">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}