import React, { useState, useEffect } from 'react';

export const SearchSpace: React.FC = () => {
    const [n, setN] = useState(4);
    const [paths, setPaths] = useState(0);
    const [time, setTime] = useState('');
    const [barHeight, setBarHeight] = useState(0);

    // Factorial function
    const factorial = (num: number): number => {
        if (num <= 1) return 1;
        return num * factorial(num - 1);
    };

    // Format time
    const formatTime = (ms: number): string => {
        if (ms < 1000) return `${ms.toFixed(0)} ms`;
        const s = ms / 1000;
        if (s < 60) return `${s.toFixed(1)} seconds`;
        const m = s / 60;
        if (m < 60) return `${m.toFixed(1)} minutes`;
        const h = m / 60;
        if (h < 24) return `${h.toFixed(1)} hours`;
        const d = h / 24;
        if (d < 365) return `${d.toFixed(1)} days`;
        const y = d / 365;
        if (y < 1000) return `${y.toFixed(1)} years`;
        return `${(y / 1000).toFixed(1)} millennia`;
    };

    useEffect(() => {
        // Hamiltonian path on complete graph K_n has (n-1)! / 2 unique paths (undirected)
        // Or just n! permutations if we consider order matters and start anywhere.
        // The prompt says "Number of possible paths = n!". Let's stick to that for simplicity/impact.
        const numPaths = factorial(n);
        setPaths(numPaths);

        // Assume 1 microsecond per check (1e-6 seconds = 0.001 ms)
        // Prompt says "1 microsecond per path"
        const timeMs = numPaths * 0.001;
        setTime(formatTime(timeMs));

        // Calculate bar height logarithmically for visualization
        // Max N=14 -> 14! approx 8.7e10
        // Log10(14!) approx 10.9
        // Log10(4!) approx 1.38
        const logVal = Math.log10(numPaths);
        const maxLog = Math.log10(factorial(14));
        const heightPercent = (logVal / maxLog) * 100;
        setBarHeight(heightPercent);

    }, [n]);

    return (
        <section id="scaling" className="section station">
            <div className="section-inner">
                <div className="section-header">
                    <div>
                        <p className="eyebrow">Station 2</p>
                        <h2 className="section-title">Search Space Growth</h2>
                        <p className="muted">Feel how small increases in cities explode the work required.</p>
                    </div>
                    <div className="station-controls">
                        {/* Optional clear button */}
                    </div>
                </div>

                <div className="grid-2col gap">
                    <div className="card tall">
                        <div className="control-grid">
                            <label className="label" htmlFor="sw-n">Number of Cities (n)</label>
                            <input
                                id="sw-n"
                                type="range"
                                min="4"
                                max="14"
                                value={n}
                                onChange={(e) => setN(parseInt(e.target.value))}
                                className="range"
                            />
                            <div className="muted text-xs mt-2">Value: <span id="sw-n-val" className="text-accent font-bold">{n}</span></div>

                            <div className="mt-8">
                                <div className="label">Possible Paths (n!)</div>
                                <div className="code-block text-lg w-full text-right">{paths.toLocaleString()}</div>
                            </div>

                            <div className="mt-4">
                                <div className="label">Time to check all (at 1µs/path)</div>
                                <div className="code-block text-lg w-full text-right" style={{ color: n > 11 ? '#f87171' : 'var(--ivory)' }}>
                                    {time}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="card tall flex flex-col justify-end pb-8 px-8 relative overflow-hidden">
                        {/* Background fog effect based on N */}
                        <div
                            className="absolute inset-0 pointer-events-none transition-opacity duration-1000"
                            style={{
                                background: `radial-gradient(circle, rgba(255,255,255,${n / 30}) 1px, transparent 1px)`,
                                backgroundSize: `${20 - n}px ${20 - n}px`,
                                opacity: n / 14
                            }}
                        ></div>

                        <div className="flex items-end justify-around h-64 gap-8 z-10">
                            {/* Bar A: Check one path */}
                            <div className="flex flex-col items-center w-full">
                                <div className="mb-2 text-xs text-muted text-center">Check One</div>
                                <div
                                    className="w-full bg-accent rounded-t-md transition-all duration-300"
                                    style={{ height: '4px', opacity: 0.8 }}
                                ></div>
                                <div className="mt-2 text-xs font-mono">1 µs</div>
                            </div>

                            {/* Bar B: Try all paths */}
                            <div className="flex flex-col items-center w-full h-full justify-end">
                                <div className="mb-2 text-xs text-muted text-center">Check All</div>
                                <div
                                    className="w-full rounded-t-md transition-all duration-500 relative"
                                    style={{
                                        height: `${Math.max(4, barHeight)}%`,
                                        background: n > 11 ? 'linear-gradient(to top, #ef4444, #f87171)' : 'linear-gradient(to top, var(--accent), var(--accent-2))'
                                    }}
                                >
                                    {/* Overflow indicator if huge */}
                                    {n > 12 && (
                                        <div className="absolute -top-6 left-0 right-0 text-center text-red-400 text-xs animate-bounce">
                                            EXPLOSION
                                        </div>
                                    )}
                                </div>
                                <div className="mt-2 text-xs font-mono">{time}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
