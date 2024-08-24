'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

// Update the Node interface
interface Node extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  type: string;
}

// Update the Link interface
interface Link extends d3.SimulationLinkDatum<Node> {
  type: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function EntityGraph({ data }: { data: GraphData }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (data && svgRef.current) {
      const svg = d3.select(svgRef.current);
      const width = svg.node()?.getBoundingClientRect().width || 0;
      const height = svg.node()?.getBoundingClientRect().height || 0;

      svg.selectAll('*').remove();

      // Create simulation
      const simulation = d3.forceSimulation<Node>(data.nodes)
        .force('link', d3.forceLink<Node, Link>(data.links).id(d => d.id))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2));

      // Add links
      const links = svg
        .selectAll('line')
        .data(data.links)
        .enter()
        .append('line')
        .attr('stroke', 'black')
        .attr('stroke-width', 2);

      // Add nodes
      const nodes = svg
        .selectAll('circle')
        .data(data.nodes)
        .enter()
        .append('circle')
        .attr('r', 10)
        .attr('fill', (d) => d.type === 'entity' ? 'blue' : 'green');

      // Update positions on tick
      simulation.on('tick', () => {
        links
          .attr('x1', d => (d.source as Node).x!)
          .attr('y1', d => (d.source as Node).y!)
          .attr('x2', d => (d.target as Node).x!)
          .attr('y2', d => (d.target as Node).y!);

        nodes
          .attr('cx', d => d.x!)
          .attr('cy', d => d.y!);
      });
    }
  }, [data]);

  return (
    <div className="w-full h-full bg-gray-900">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}