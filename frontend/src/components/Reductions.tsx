import React, { useState } from 'react';

type Problem = '3SAT' | 'CLIQUE' | 'PATH';

interface ReductionInfo {
    source: Problem;
    target: Problem;
    description: string;
    sizeEffect: string;
}

const reductions: ReductionInfo[] = [
    { source: '3SAT', target: 'CLIQUE', description: 'Transform clauses into groups of nodes. Edges connect compatible literals.', sizeEffect: 'n variables, m clauses → 3m nodes' },
    { source: 'CLIQUE', target: '3SAT', description: 'Possible but complex (NP-Complete to NP-Complete).', sizeEffect: 'Polynomial blowup' },
    { source: '3SAT', target: 'PATH', description: 'Variables become diamond gadgets, clauses become check nodes.', sizeEffect: 'Large constant factor growth' },
];

export const Reductions: React.FC = () => {
    const [selectedSource, setSelectedSource] = useState<Problem | null>(null);
    const [selectedTarget, setSelectedTarget] = useState<Problem | null>(null);
    const [reductionInfo, setReductionInfo] = useState<ReductionInfo | null>(null);

    // Micro-task state
    const [taskStep, setTaskStep] = useState<'intro' | 'challenge' | 'success'>('intro');
    const [selectedGadget, setSelectedGadget] = useState<number | null>(null);
    const [feedback, setFeedback] = useState('');

    const handleNodeClick = (problem: Problem) => {
        if (!selectedSource) {
            setSelectedSource(problem);
            setReductionInfo(null);
        } else if (selectedSource === problem) {
            setSelectedSource(null);
            setSelectedTarget(null);
            setReductionInfo(null);
        } else {
            setSelectedTarget(problem);
            const info = reductions.find(r => r.source === selectedSource && r.target === problem);
            if (info) {
                setReductionInfo(info);
            } else {
                setReductionInfo({ source: selectedSource, target: problem, description: 'Reduction exists but not detailed here.', sizeEffect: 'Polynomial' });
            }
        }
    };

    const handleGadgetSelect = (id: number) => {
        setSelectedGadget(id);
        if (id === 2) { // Correct gadget
            setFeedback('Correct! This gadget forces at least one input to be true.');
            setTaskStep('success');
        } else {
            setFeedback('Incorrect. This gadget allows all inputs to be false, breaking the clause logic.');
        }
    };

    return (
        <section id="conveyor" className="section station">
            <div className="section-inner">
                <div className="section-header">
                    <div>
                        <p className="eyebrow">Station 3</p>
                        <h2 className="section-title">Reductions Map</h2>
                        <p className="muted">Solving one efficiently implies solving many.</p>
                    </div>
                </div>

                <div className="grid-2col gap">
                    {/* Part A: Problem Graph */}
                    <div className="card tall">
                        <div className="card-head">
                            <div className="card-kicker">Part A</div>
                            <div className="card-title">The Web of Reductions</div>
                        </div>
                        <div className="panel flex flex-col items-center justify-center min-h-[300px] relative">
                            <p className="muted mb-4 text-center">Select a Source then a Target to see the link.</p>

                            <div className="flex justify-between w-full px-8 mb-12">
                                <button
                                    onClick={() => handleNodeClick('3SAT')}
                                    className={`chip ${selectedSource === '3SAT' ? 'bg-accent text-black' : selectedTarget === '3SAT' ? 'bg-accent-2 text-black' : 'ghost'} text-lg px-6 py-3`}
                                >
                                    3-SAT
                                </button>
                                <button
                                    onClick={() => handleNodeClick('CLIQUE')}
                                    className={`chip ${selectedSource === 'CLIQUE' ? 'bg-accent text-black' : selectedTarget === 'CLIQUE' ? 'bg-accent-2 text-black' : 'ghost'} text-lg px-6 py-3`}
                                >
                                    CLIQUE
                                </button>
                            </div>
                            <div className="flex justify-center w-full">
                                <button
                                    onClick={() => handleNodeClick('PATH')}
                                    className={`chip ${selectedSource === 'PATH' ? 'bg-accent text-black' : selectedTarget === 'PATH' ? 'bg-accent-2 text-black' : 'ghost'} text-lg px-6 py-3`}
                                >
                                    HAM-PATH
                                </button>
                            </div>

                            {/* Arrows visualization (simplified) */}
                            <svg className="absolute inset-0 pointer-events-none" width="100%" height="100%">
                                <defs>
                                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                                        <path d="M0,0 L0,6 L9,3 z" fill="var(--muted)" />
                                    </marker>
                                </defs>
                                {/* 3SAT -> CLIQUE */}
                                <line x1="20%" y1="80" x2="80%" y2="80" stroke="var(--line)" strokeWidth="2" markerEnd="url(#arrow)" />
                                {/* 3SAT -> PATH */}
                                <line x1="20%" y1="100" x2="50%" y2="220" stroke="var(--line)" strokeWidth="2" markerEnd="url(#arrow)" />
                                {/* CLIQUE -> 3SAT */}
                                {/* PATH -> 3SAT (not shown for simplicity) */}
                            </svg>

                            {reductionInfo && (
                                <div className="mt-8 p-4 bg-white/5 rounded-lg border border-white/10 w-full reveal-on">
                                    <div className="font-bold text-accent mb-1">{reductionInfo.source} &rarr; {reductionInfo.target}</div>
                                    <div className="text-sm text-ivory mb-2">{reductionInfo.description}</div>
                                    <div className="text-xs text-muted font-mono">Size: {reductionInfo.sizeEffect}</div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Part B: Micro Task */}
                    <div className="card tall">
                        <div className="card-head">
                            <div className="card-kicker">Part B</div>
                            <div className="card-title">Reduction Engineer</div>
                        </div>
                        <div className="panel">
                            {taskStep === 'intro' && (
                                <div className="text-center py-8">
                                    <p className="mb-4">To prove 3-SAT is hard, we must translate it into other problems.</p>
                                    <p className="mb-6 text-muted">Your task: Choose the correct "Gadget" to represent a logical OR clause (A or B or C) using only graph connections.</p>
                                    <button onClick={() => setTaskStep('challenge')} className="btn primary">Start Task</button>
                                </div>
                            )}

                            {taskStep !== 'intro' && (
                                <div>
                                    <div className="label mb-4">Clause: (x1 OR x2 OR x3) must be TRUE.</div>
                                    <div className="grid grid-cols-1 gap-4">
                                        {[1, 2, 3].map(id => (
                                            <button
                                                key={id}
                                                onClick={() => handleGadgetSelect(id)}
                                                className={`p-4 border rounded-lg text-left transition-all ${selectedGadget === id ? 'border-accent bg-accent/10' : 'border-white/10 hover:border-white/30'}`}
                                            >
                                                <div className="font-bold mb-1">Gadget {id}</div>
                                                <div className="text-xs text-muted">
                                                    {id === 1 ? 'Three disconnected nodes.' :
                                                        id === 2 ? 'Three nodes connected in a triangle (Clique).' :
                                                            'Three nodes in a line.'}
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                    {feedback && (
                                        <div className={`mt-4 p-3 rounded border ${taskStep === 'success' ? 'border-green-500/30 bg-green-500/10 text-green-200' : 'border-red-500/30 bg-red-500/10 text-red-200'}`}>
                                            {feedback}
                                        </div>
                                    )}
                                    {taskStep === 'success' && (
                                        <div className="mt-4 text-center animate-pulse text-accent font-bold">
                                            Reduction Complete! You unlocked "NP-Complete".
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
