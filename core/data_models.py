"""
Data model classes for the np-hard-lab project.

This module defines the core data structures used throughout the system
for representing problem instances, benchmark results, and algorithm configurations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Type
from core.base_solver import BaseSolver


@dataclass
class ProblemInstance:
    """
    Represents a problem instance for benchmarking.
    
    This class encapsulates all the information needed to describe a specific
    problem instance, including its type, size, parameters, and actual data.
    """
    problem_type: str
    """The type of problem (e.g., 'SAT', 'SubsetSum', 'TSP')"""
    
    size: int
    """The size of the problem instance (e.g., number of variables, cities, etc.)"""
    
    parameters: Dict[str, Any]
    """Problem-specific parameters used during generation"""
    
    data: Any
    """The actual problem data (e.g., clauses for SAT, distances for TSP)"""
    
    metadata: Dict[str, Any]
    """Additional metadata about the problem instance"""


@dataclass
class BenchmarkResult:
    """
    Represents the result of running a benchmark on a problem instance.
    
    This class captures all relevant information about a benchmark run,
    including timing, solution status, and resource usage.
    """
    algorithm_name: str
    """Name of the algorithm that was benchmarked"""
    
    problem_instance: ProblemInstance
    """The problem instance that was solved"""
    
    execution_time: float
    """Time taken to solve the problem in seconds"""
    
    solution_found: bool
    """Whether a solution was found (or if the problem was determined unsolvable)"""
    
    solution_data: Any
    """The actual solution data (if a solution was found)"""
    
    timeout_occurred: bool
    """Whether the algorithm execution was terminated due to timeout"""
    
    memory_usage: Optional[float]
    """Peak memory usage during execution in MB (if measured)"""
    
    timestamp: datetime
    """When the benchmark was executed"""


@dataclass
class AlgorithmConfig:
    """
    Configuration for an algorithm to be benchmarked.
    
    This class defines how an algorithm should be instantiated and configured
    for benchmarking purposes.
    """
    name: str
    """Human-readable name for this algorithm configuration"""
    
    solver_class: Type[BaseSolver]
    """The solver class to instantiate"""
    
    timeout_seconds: int
    """Maximum time allowed for this algorithm to run"""
    
    parameters: Dict[str, Any]
    """Algorithm-specific parameters to pass to the solver"""