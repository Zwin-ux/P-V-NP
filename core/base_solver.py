"""
Base solver interface for all algorithm implementations.

This module provides the abstract base class that all problem solvers must inherit from,
ensuring a consistent interface across different algorithm implementations.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSolver(ABC):
    """
    Abstract base class for all problem solvers.
    
    This class defines the common interface that all algorithm implementations
    must follow, enabling consistent benchmarking and comparison across different
    solving approaches.
    """
    
    @abstractmethod
    def solve(self, problem_instance: Any) -> Any:
        """
        Solve the given problem instance.
        
        Args:
            problem_instance: The problem instance to solve. The specific type
                            depends on the problem domain (SAT, Subset Sum, TSP, etc.)
        
        Returns:
            The solution to the problem instance. The return type depends on the
            specific problem domain and solver implementation.
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass
    
    @abstractmethod
    def get_complexity_class(self) -> str:
        """
        Return the theoretical computational complexity class of this algorithm.
        
        Returns:
            str: The complexity class (e.g., "P", "NP", "NP-Complete", "PSPACE")
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Return a human-readable name for this algorithm.
        
        Returns:
            str: A descriptive name for the algorithm (e.g., "Brute Force SAT Solver",
                "Dynamic Programming Subset Sum")
        
        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass