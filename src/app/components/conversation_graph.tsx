'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { zoom as d3Zoom } from 'd3';
import { useNodeSelection } from '../context/node_selection_context';
import useSound from 'use-sound';

interface Node {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
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
  const svg_ref = useRef<SVGSVGElement>(null);
  const { toggle_node_selection, selected_nodes, clear_all_selections } = useNodeSelection();
  const selection_box_ref = useRef<{ x1: number; y1: number; x2: number; y2: number } | null>(null);
  const start_point_ref = useRef<{ x: number; y: number } | null>(null);
  const is_dragging_ref = useRef(false);
  const is_clicking_ref = useRef(false);
  const [play_drag_start_sfx] = useSound('/sounds/drag-start.wav');
  const [play_drag_end_sfx] = useSound('/sounds/drag-end.wav');
  const has_played_drag_start_sfx = useRef(false);

  const handle_pointer_down = useCallback((event: PointerEvent) => {
    console.log("Pointer down event detected");
    console.log("Pointer down event detail:", event.detail);
    if (!event.shiftKey) {
      event.preventDefault();
      const [x, y] = d3.pointer(event, svg_ref.current);
      start_point_ref.current = { x, y };
      selection_box_ref.current = { x1: x, y1: y, x2: x, y2: y };
      is_clicking_ref.current = true;
      has_played_drag_start_sfx.current = false;
      const selection_rect = d3.select(svg_ref.current).select("rect");
      selection_rect
        .style("display", "block")
        .attr("x", x)
        .attr("y", y)
        .attr("width", 0)
        .attr("height", 0);
      console.log("Selection started at:", { x, y });
    }
  }, []);

  const handle_pointer_move = useCallback((event: PointerEvent) => {
    if (is_clicking_ref.current && start_point_ref.current && !event.shiftKey) {
      console.log("Pointer move event detected during selection");
      is_dragging_ref.current = true
      if (!has_played_drag_start_sfx.current) {
        play_drag_start_sfx();
        has_played_drag_start_sfx.current = true;
      }

      const [x, y] = d3.pointer(event, svg_ref.current);
      const x1 = Math.min(start_point_ref.current.x, x);
      const y1 = Math.min(start_point_ref.current.y, y);
      const x2 = Math.max(start_point_ref.current.x, x);
      const y2 = Math.max(start_point_ref.current.y, y);
      selection_box_ref.current = { x1, y1, x2, y2 };

      const selection_rect = d3.select(svg_ref.current).select("rect");
      selection_rect
        .attr("x", x1)
        .attr("y", y1)
        .attr("width", x2 - x1)
        .attr("height", y2 - y1);
      console.log("Drawing selection box:", { x1, y1, x2, y2 });
    }
  }, [play_drag_start_sfx]);

  const handle_pointer_up = useCallback((event: PointerEvent) => {
    is_clicking_ref.current = false
    if (is_dragging_ref.current && selection_box_ref.current && !event.shiftKey && data) {
      play_drag_end_sfx();
      const transform = d3.zoomTransform(svg_ref.current as any);
      console.log("Starting node selection process");
      const selected_ids = data.nodes.filter((node) => {
        const node_x = transform.applyX(node.x!);
        const node_y = transform.applyY(node.y!);
        const node_rect = { x1: node_x - 20, y1: node_y - 20, x2: node_x + 20, y2: node_y + 20 };
        console.log(`Node ${node.id} position:`, { node_x, node_y, node_rect });
        console.log(`Selection box:`, selection_box_ref.current);
        const is_selected = (
          node_rect.x1 < selection_box_ref.current!.x2 &&
          node_rect.x2 > selection_box_ref.current!.x1 &&
          node_rect.y1 < selection_box_ref.current!.y2 &&
          node_rect.y2 > selection_box_ref.current!.y1
        );
        console.log(`Node ${node.id} selected:`, is_selected);
        return is_selected;
      }).map(node => node.id);
      console.log("Selected node IDs:", selected_ids);
      selected_ids.forEach(id => {
        const node_data = { id, label: data.nodes.find(n => n.id === id)?.type || '' };
        toggle_node_selection(node_data);
      });
      console.log("Selection ended. Selected nodes:", selected_ids);
    }
    start_point_ref.current = null;
    selection_box_ref.current = null;
    is_dragging_ref.current = false;
    has_played_drag_start_sfx.current = false;
    const selection_rect = d3.select(svg_ref.current).select("rect");
    selection_rect.style("display", "none");
  }, [data, toggle_node_selection, play_drag_end_sfx]);

  useEffect(() => {
    console.log("ConversationGraph component is rendering with data:");
    if (data && svg_ref.current) {
      const svg = d3.select(svg_ref.current);
      svg.selectAll("*").remove();

      const width = svg.node()?.getBoundingClientRect().width || 800;
      const height = svg.node()?.getBoundingClientRect().height || 600;

      const g = svg.append("g");

      const ticked = () => {
        link
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);

        node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
      };

      const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id((d: any) => d.id))
        .force("charge", d3.forceManyBody().strength(-1000))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

      const link = g.append("g")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-width", 1);

      const node = g.append("g")
        .selectAll("g")
        .data(data.nodes)
        .enter().append("g")
        .on("click", (event, d) => {
          play_drag_end_sfx();
          const node_data = { id: d.id, label: d.type };
          toggle_node_selection(node_data);
        })
        .call(d3.drag<SVGGElement, Node>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }) as any);

      node.append("circle")
        .attr("r", 20)
        .attr("fill", (d) => get_node_color(d))
        .style("filter", "url(#glow)");

      node.append("text")
        .attr("dy", 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-size", "10px")
        .text((d) => d.label.split(':')[0]);

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

      const zoom = d3Zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
          if (event.sourceEvent && event.sourceEvent.shiftKey) {
            g.attr("transform", event.transform);
          }
        });

      svg.call(zoom as any);

      // Draw selection box
      svg.append("rect")
        .attr("fill", "rgba(255, 255, 0, 0.2)")
        .attr("stroke", "yellow")
        .attr("stroke-dasharray", "4")
        .attr("stroke-width", 1)
        .style("display", "none")
        .attr("pointer-events", "none");

      // Add event listeners
      svg.on("pointerdown", handle_pointer_down);
      svg.on("pointermove", handle_pointer_move);
      svg.on("pointerup", handle_pointer_up);

      // Cleanup function
      return () => {
        svg.on("pointerdown", null);
        svg.on("pointermove", null);
        svg.on("pointerup", null);
      };
    } else {
      console.log("Data or SVG reference is missing");
    }
  }, [data, selected_nodes]);

  useEffect(() => {
    if (svg_ref.current) {
      const svg = d3.select(svg_ref.current);
      svg.selectAll("g > circle").attr("fill", (d: any) => get_node_color(d));
    }
  }, [selected_nodes]); // Update node colors when selected_nodes changes

  const get_node_color = (d: Node) => {
    if (selected_nodes.some(node => node.id === d.id)) return 'yellow';
    if (d.type === 'agent') return 'red';
    if (d.type === 'user') return 'blue';
    if (d.type === 'message') return 'lightblue';
    return 'orange';
  };
  const handle_div_click = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    console.log("Div click event detail:", event.detail);
    if(event.detail==2) {
      play_drag_end_sfx();
      clear_all_selections();
      console.log("All nodes deselected due to div click.");
    }
  }, []);

  return (
    <div 
      className="w-full h-full bg-gray-900" 
      onClick={handle_div_click}
    >
      <svg ref={svg_ref} className="w-full h-full" />
    </div>
  );
}