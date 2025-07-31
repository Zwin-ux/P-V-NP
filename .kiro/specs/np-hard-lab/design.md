# Design Document

## Overview

The np-hard-lab is designed as a modular educational testbed that demonstrates computational complexity concepts through practical implementations. The system follows a layered architecture with separate modules for problem generation, solving algorithms, benchmarking, visualization, and educational content. The design emphasizes code clarity, extensibility, and educational value while maintaining performance measurement accuracy.

## Architecture

The system uses a modular architecture with the following key components:

```
np-hard-lab/
├── core/                    # Core algorithm implementations
│   ├── sat_solver.py       # SAT solving algorithms
│   ├── subset_sum.py       # Subset sum algorithms  
│   ├── traveling_salesman.py # TSP algorithms
│   └── base_solver.py      # Common solver interface
├── generators/             # Problem instance generators
│   ├── sat_generator.py    # 3-SAT instance generation
│   ├── subset_generator.py # Subset sum generation
│   └── tsp_generator.py    # TSP instance generation
├── benchmarks/             # Benchmarking and timing
│   ├── benchmark_runner.py # Main benchmarking engine
│   ├── results_storage.py  # Results persistence
│   └── timeout_manager.py  # Timeout handling
├── visualization/          # Data visualization
│   ├── graph_generator.py  # Performance graphs
│   └── report_builder.py   # HTML/markdown reports
├── demos/                  # Standalone demonstrations
│   ├── sat_demo.py         # SAT solver comparison
│   ├── subset_demo.py      # Subset sum comparison
│   └── tsp_demo.py         # TSP comparison
├── docs/                   # Educational documentation
│   └── theory/             # P vs NP explanations
├── tests/                  # Unit and integration tests
└── data/                   # Generated datasets and results
```

## Components and Interfaces

### Base Solver Interface

All algorithm implementations inherit from a common `BaseSolver` interface:

```python
class BaseSolver:
    def solve(self, problem_instance):
        """Solve the given problem instance"""
        pass
    
    def get_complexity_class(self):
        """Return theoretical complexity (P, NP, etc.)"""
        pass
    
    def get_algorithm_name(self):
        """Return human-readable algorithm name"""
        pass
```

### Problem Generators

Each problem type has a dedicated generator with configurable parameters:

- **SAT Generator**: Creates 3-SAT instances with configurable variable/clause ratios
- **Subset Sum Generator**: Generates sets with configurable sizes and target values
- **TSP Generator**: Creates distance matrices with various city configurations

### Benchmarking Engine

The `BenchmarkRunner` coordinates timing experiments:

- Manages multiple algorithm comparisons
- Implements timeout mechanisms
- Collects performance metrics
- Handles result persistence

### Visualization System

The visualization component creates:

- Time vs problem size graphs
- Algorithm comparison charts
- Scaling behavior demonstrations
- Interactive HTML reports

## Data Models

### Problem Instance

```python
@dataclass
class ProblemInstance:
    problem_type: str
    size: int
    parameters: Dict[str, Any]
    data: Any
    metadata: Dict[str, Any]
```

### Benchmark Result

```python
@dataclass
class BenchmarkResult:
    algorithm_name: str
    problem_instance: ProblemInstance
    execution_time: float
    solution_found: bool
    solution_data: Any
    timeout_occurred: bool
    memory_usage: Optional[float]
    timestamp: datetime
```

### Algorithm Configuration

```python
@dataclass
class AlgorithmConfig:
    name: str
    solver_class: Type[BaseSolver]
    timeout_seconds: int
    parameters: Dict[str, Any]
```

## Error Handling

### Timeout Management

- Implement configurable timeouts for each algorithm
- Graceful handling of timeout scenarios
- Clear indication when algorithms exceed time limits
- Automatic fallback to smaller problem sizes if needed

### Input Validation

- Validate problem generator parameters
- Ensure problem instances are well-formed
- Handle edge cases in algorithm inputs
- Provide meaningful error messages for invalid configurations

### Resource Management

- Monitor memory usage during algorithm execution
- Implement safeguards against excessive resource consumption
- Clean up temporary data structures
- Handle system resource limitations gracefully

## Testing Strategy

### Unit Testing

- Test each algorithm implementation for correctness
- Verify problem generators produce valid instances
- Test benchmarking components in isolation
- Validate visualization output formats

### Integration Testing

- Test complete benchmark workflows
- Verify data flow between components
- Test timeout mechanisms under load
- Validate result persistence and retrieval

### Performance Testing

- Establish baseline performance metrics
- Test scaling behavior across problem sizes
- Verify timeout mechanisms work correctly
- Monitor memory usage patterns

### Educational Content Testing

- Verify documentation accuracy
- Test demo scripts for reliability
- Validate example outputs
- Ensure educational explanations are clear

## Implementation Considerations

### Algorithm Selection

**SAT Solvers:**
- Brute-force: Exhaustive truth table evaluation
- Optimized: DPLL-style algorithm with unit propagation and pure literal elimination

**Subset Sum:**
- Brute-force: Generate all possible subsets
- Optimized: Dynamic programming approach

**Traveling Salesman:**
- Brute-force: Try all permutations
- Optimized: Nearest neighbor heuristic or branch-and-bound

### Performance Measurement

- Use high-precision timing (time.perf_counter)
- Implement warm-up runs to stabilize measurements
- Account for system variability in timing
- Provide statistical analysis of multiple runs

### Scalability Design

- Design for easy addition of new problems
- Support pluggable algorithm implementations
- Enable configuration-driven benchmarking
- Facilitate extension with new visualization types

### Educational Focus

- Prioritize code readability over micro-optimizations
- Include extensive comments explaining algorithmic choices
- Provide clear examples and demonstrations
- Structure code to highlight complexity differences