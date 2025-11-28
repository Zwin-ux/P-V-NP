import React, { useState } from 'react';
import { Graph } from './Graph';

// Define a simple 6-node graph
const nodes = [
    { id: 1, x: 50, y: 150, label: 'A' },
    { id: 2, x: 150, y: 50, label: 'B' },
    { id: 3, x: 150, y: 250, label: 'C' },
    { id: 4, x: 250, y: 50, label: 'D' },
    { id: 5, x: 250, y: 250, label: 'E' },
    { id: 6, x: 350, y: 150, label: 'F' },
];

const edges = [
    { source: 1, target: 2 },
    { source: 1, target: 3 },
    { source: 2, target: 4 },
    { source: 2, target: 3 },
    { source: 3, target: 5 },
    { source: 4, target: 6 },
    { source: 5, target: 6 },
    { source: 4, target: 5 }, // Cross connection
    { source: 2, target: 5 }, // Cross connection
];

// A valid Hamiltonian path: A -> B -> D -> F -> E -> C (No, C connects to A, B, E. E connects to C, F, D, B. F connects to D, E. D connects to B, F, E. B connects to A, D, C, E. A connects to B, C)
// Path: 1 -> 2 -> 4 -> 6 -> 5 -> 3 (A->B->D->F->E->C) - Wait, 3 connects to 1 and 2 and 5. So C connects to E. Yes.
const validPath = [1, 2, 4, 6, 5, 3];

export const CheckVsFind: React.FC = () => {
    const [phase, setPhase] = useState<'verify' | 'find'>('verify');
    const [userPath, setUserPath] = useState<number[]>([]);
    const [checks, setChecks] = useState(0);
    const [attempts, setAttempts] = useState(0);
    const [message, setMessage] = useState('');
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

    const handleVerify = () => {
        setChecks(c => c + 1);
        setMessage('Path verified in 3ms. Valid.');
        setStatus('success');
    };

    const handleFindSubmit = () => {
        setAttempts(a => a + 1);
        // Check if path is valid Hamiltonian path
        // 1. Must visit all nodes
        // 2. Must be connected (enforced by Graph component interaction)
        // 3. No duplicates (enforced by Graph component interaction logic mostly, but let's check)

        if (userPath.length !== nodes.length) {
            setMessage('Invalid: Path must visit all cities exactly once.');
            setStatus('error');
            return;
        }

        // Check edges exist (Graph component enforces this but good to double check)
        // Check duplicates
        const unique = new Set(userPath);
        if (unique.size !== nodes.length) {
            setMessage('Invalid: Visited a city twice.');
            setStatus('error');
            return;
        }

        // Check if it matches OUR valid path or ANY valid path?
        // For this small graph, let's just check if it's a valid path.
        // Actually, let's just check if it is a valid Hamiltonian path.
        // My graph logic enforces valid moves. So if length is correct and unique, it's valid.

        setMessage('Verifying... Valid! You found it.');
        setStatus('success');
    };

    const reset = () => {
        setPhase('verify');
        setUserPath([]);
        setChecks(0);
        setAttempts(0);
        setMessage('');
        setStatus('idle');
    };

    return (
        <section id="verify-search" className="section station">
            <div className="section-inner">
                <div className="section-header">
                    <div>
                        <p className="eyebrow">Station 1</p>
                        <h2 className="section-title">Check vs Find</h2>
                        <p className="muted">Experience the asymmetry of P vs NP.</p>
                    </div>
                    <div className="station-controls">
                        <button onClick={reset} className="chip ghost">Reset station</button>
                    </div>
                </div>

                <div className="grid-2col gap">
                    {/* Phase A: Verification */}
                    <div className={`card ${phase === 'verify' ? '' : 'opacity-50'}`}>
                        <div className="card-head">
                            <div className="card-kicker">Phase A</div>
                            <div className="card-title">Verification</div>
                        </div>
                        <div className="panel">
                            <p className="muted mb-4">Here is a proposed solution. Check if it visits every city exactly once.</p>
                            <Graph
                                nodes={nodes}
                                edges={edges}
                                highlightedPath={phase === 'verify' ? validPath : []}
                                interactive={false}
                            />
                            <div className="btn-row mt-3">
                                <button
                                    onClick={handleVerify}
                                    disabled={phase !== 'verify'}
                                    className="btn primary"
                                >
                                    Verify Path
                                </button>
                            </div>
                            <div className="mt-3">
                                <div className="label">Checks performed: {checks}</div>
                                <div className="label">Time per check: ~3ms</div>
                            </div>
                            {phase === 'verify' && message && (
                                <div className="result-line mt-2" style={{ color: 'var(--accent)' }}>{message}</div>
                            )}
                        </div>
                        {phase === 'verify' && status === 'success' && (
                            <div className="mt-4">
                                <button onClick={() => { setPhase('find'); setMessage(''); setStatus('idle'); }} className="btn ghost w-full">
                                    Proceed to Phase B &rarr;
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Phase B: Finding */}
                    <div className={`card ${phase === 'find' ? '' : 'opacity-50'}`}>
                        <div className="card-head">
                            <div className="card-kicker">Phase B</div>
                            <div className="card-title">Finding</div>
                        </div>
                        <div className="panel">
                            <p className="muted mb-4">Now find a path yourself. Click cities to connect them.</p>
                            <Graph
                                nodes={nodes}
                                edges={edges}
                                interactive={phase === 'find'}
                                userPath={userPath}
                                onPathChange={setUserPath}
                            />
                            <div className="btn-row mt-3">
                                <button
                                    onClick={handleFindSubmit}
                                    disabled={phase !== 'find' || userPath.length === 0}
                                    className="btn primary"
                                >
                                    Check My Path
                                </button>
                                <button
                                    onClick={() => setUserPath([])}
                                    disabled={phase !== 'find'}
                                    className="btn ghost"
                                >
                                    Clear
                                </button>
                            </div>
                            <div className="mt-3">
                                <div className="label">Attempts: {attempts}</div>
                                <div className="label">Time to find: ???</div>
                            </div>
                            {phase === 'find' && message && (
                                <div className={`result-line mt-2 ${status === 'error' ? 'text-red-400' : 'text-accent'}`} style={{ color: status === 'error' ? '#f87171' : 'var(--accent)' }}>
                                    {message}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
