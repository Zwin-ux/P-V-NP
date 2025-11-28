import React from 'react';

interface Node {
    id: number;
    x: number;
    y: number;
    label: string;
}

interface Edge {
    source: number;
    target: number;
}

interface GraphProps {
    nodes: Node[];
    edges: Edge[];
    highlightedPath?: number[]; // Array of node IDs
    interactive?: boolean;
    onPathChange?: (path: number[]) => void;
    userPath?: number[];
}

export const Graph: React.FC<GraphProps> = ({
    nodes,
    edges,
    highlightedPath = [],
    interactive = false,
    onPathChange,
    userPath = []
}) => {
    const radius = 20;

    const handleNodeClick = (nodeId: number) => {
        if (!interactive || !onPathChange) return;

        // If node is already in path, remove it and everything after (backtrack)
        const index = userPath.indexOf(nodeId);
        if (index !== -1) {
            onPathChange(userPath.slice(0, index + 1));
        } else {
            // Add to path if connected to last node
            if (userPath.length === 0) {
                onPathChange([nodeId]);
            } else {
                const lastNode = userPath[userPath.length - 1];
                // Check if edge exists
                const hasEdge = edges.some(e =>
                    (e.source === lastNode && e.target === nodeId) ||
                    (e.source === nodeId && e.target === lastNode)
                );
                if (hasEdge) {
                    onPathChange([...userPath, nodeId]);
                }
            }
        }
    };

    return (
        <svg width="100%" height="300" viewBox="0 0 400 300" className="graph-svg">
            {/* Edges */}
            {edges.map((edge, i) => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                if (!source || !target) return null;

                // Check if this edge is part of the highlighted path
                let isHighlighted = false;
                for (let j = 0; j < highlightedPath.length - 1; j++) {
                    if ((highlightedPath[j] === edge.source && highlightedPath[j + 1] === edge.target) ||
                        (highlightedPath[j] === edge.target && highlightedPath[j + 1] === edge.source)) {
                        isHighlighted = true;
                        break;
                    }
                }

                // Check if part of user path
                let isUserPath = false;
                for (let j = 0; j < userPath.length - 1; j++) {
                    if ((userPath[j] === edge.source && userPath[j + 1] === edge.target) ||
                        (userPath[j] === edge.target && userPath[j + 1] === edge.source)) {
                        isUserPath = true;
                        break;
                    }
                }

                return (
                    <line
                        key={`edge-${i}`}
                        x1={source.x}
                        y1={source.y}
                        x2={target.x}
                        y2={target.y}
                        stroke={isHighlighted || isUserPath ? "var(--accent)" : "rgba(255,255,255,0.1)"}
                        strokeWidth={isHighlighted || isUserPath ? 4 : 2}
                        strokeLinecap="round"
                    />
                );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
                const isSelected = userPath.includes(node.id) || highlightedPath.includes(node.id);
                const isLast = userPath.length > 0 && userPath[userPath.length - 1] === node.id;

                return (
                    <g
                        key={`node-${node.id}`}
                        onClick={() => handleNodeClick(node.id)}
                        style={{ cursor: interactive ? 'pointer' : 'default' }}
                    >
                        <circle
                            cx={node.x}
                            cy={node.y}
                            r={radius}
                            fill={isSelected ? "var(--accent)" : "var(--panel)"}
                            stroke={isSelected ? "var(--accent)" : "rgba(255,255,255,0.3)"}
                            strokeWidth="2"
                            className={isLast ? "pulse-node" : ""}
                        />
                        <text
                            x={node.x}
                            y={node.y}
                            dy=".35em"
                            textAnchor="middle"
                            fill={isSelected ? "#000" : "var(--ivory)"}
                            fontWeight="bold"
                            pointerEvents="none"
                        >
                            {node.label}
                        </text>
                        {/* Order badge for user path */}
                        {userPath.includes(node.id) && (
                            <circle cx={node.x + 14} cy={node.y - 14} r="8" fill="var(--night)" />
                        )}
                        {userPath.includes(node.id) && (
                            <text x={node.x + 14} y={node.y - 14} dy=".35em" textAnchor="middle" fill="var(--accent)" fontSize="10">
                                {userPath.indexOf(node.id) + 1}
                            </text>
                        )}
                    </g>
                );
            })}
        </svg>
    );
};
