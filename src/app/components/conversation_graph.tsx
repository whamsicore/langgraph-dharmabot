'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { zoom as d3Zoom } from 'd3';

interface Node {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
}

interface Link {
  source: string | Node;
  target: string | Node;
  type: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function ConversationGraph({ data }: { data: GraphData }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (data && svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      const width = svg.node()?.getBoundingClientRect().width || 800;
      const height = svg.node()?.getBoundingClientRect().height || 600;

      const g = svg.append("g");

      // Define functions at the beginning of the useEffect
      const ticked = () => {
        link.select("line")
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);

        link.select("text")
          .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
          .attr("y", (d: any) => (d.source.y + d.target.y) / 2);

        node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
      };

      const drag_started = (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      };

      const dragged = (event: any, d: any) => {
        d.fx = event.x;
        d.fy = event.y;
      };

      const drag_ended = (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      };

      const get_node_color = (d: Node) => {
        if (d.type === 'agent') return 'red';
        if (d.type === 'user') return 'blue';
        if (d.type === 'message') return 'lightblue'; // Updated color for message nodes
        return 'orange'; // for conversation nodes
      };

      // Add zoom functionality
      const zoom = d3Zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
          g.attr("transform", event.transform);
        });

      svg.call(zoom as any);

      const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id((d: any) => d.id))
        .force("charge", d3.forceManyBody().strength(-1000))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

      const link = g.append("g")
        .selectAll("g")
        .data(data.links)
        .enter().append("g");

      link.append("line")
        .attr("stroke", "#999")
        .attr("stroke-width", 1);

      link.append("text")
        .attr("dy", -2)
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-size", "6px")
        .text((d) => d.type);

      const node = g.append("g")
        .selectAll("g")
        .data(data.nodes)
        .enter().append("g")
        .call(d3.drag<SVGGElement, Node>()
          .on("start", drag_started)
          .on("drag", dragged)
          .on("end", drag_ended) as any);

      node.append("circle")
        .attr("r", 20)
        .attr("fill", (d) => get_node_color(d))
        .style("filter", "url(#glow)");

      node.append("text")
        .attr("dy", 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-size", "10px")
        .text((d) => d.label.split(':')[0]); // Remove colon from message labels

      // Add glow filter
      const defs = svg.append("defs");
      const filter = defs.append("filter")
        .attr("id", "glow");
      filter.append("feGaussianBlur")
        .attr("stdDeviation", "3.5")
        .attr("result", "coloredBlur");
      const feMerge = filter.append("feMerge");
      feMerge.append("feMergeNode")
        .attr("in", "coloredBlur");
      feMerge.append("feMergeNode")
        .attr("in", "SourceGraphic");
    }
  }, [data]);

  return (
    <div className="w-full h-full bg-gray-900">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}