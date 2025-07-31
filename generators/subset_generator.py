"""
Subset Sum problem instance generator.

This module provides functionality to generate Subset Sum problem instances
with configurable parameters for educational and benchmarking purposes.
"""

import random
from typing import List, Dict, Any, Set
from core.data_models import ProblemInstance


class SubsetSumInstance:
    """
    Represents a Subset Sum problem instance.
    
    A Subset Sum instance consists of a set of positive integers and a target sum.
    The goal is to find a subset of the integers that sum exactly to the target.
    """
    
    def __init__(self, numbers: List[int], target: int):
        """
        Initialize a Subset Sum instance.
        
        Args:
            numbers: List of positive integers
            target: Target sum to achieve
        """
        self.numbers = numbers
        self.target = target
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the Subset Sum instance."""
        result = f"Subset Sum instance with {len(self.numbers)} numbers, target = {self.target}:\n"
        result += f"  Numbers: {self.numbers}\n"
        result += f"  Target: {self.target}\n"
        return result


def generate_subset_sum_instance(set_size: int, max_value: int = None, target: int = None, seed: int = None) -> ProblemInstance:
    """
    Generate a random Subset Sum problem instance.
    
    Creates a Subset Sum instance with the specified set size. If target is not provided,
    a random target will be generated based on the sum of a random subset.
    
    Args:
        set_size: Number of integers in the set (must be >= 1)
        max_value: Maximum value for generated integers (defaults to set_size * 10)
        target: Target sum (if None, will be generated randomly)
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated Subset Sum data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if set_size < 1:
        raise ValueError("Set size must be at least 1")
    if max_value is not None and max_value < 1:
        raise ValueError("Maximum value must be at least 1")
    if target is not None and target < 0:
        raise ValueError("Target must be non-negative")
    
    # Set default max_value if not provided
    if max_value is None:
        max_value = set_size * 10
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate random positive integers
    numbers = [random.randint(1, max_value) for _ in range(set_size)]
    
    # Generate target if not provided
    if target is None:
        # Create a random subset and use its sum as the target
        # This ensures the instance is solvable
        subset_size = random.randint(1, min(set_size, 5))  # Limit subset size for reasonable targets
        subset_indices = random.sample(range(set_size), subset_size)
        target = sum(numbers[i] for i in subset_indices)
    
    # Create the Subset Sum instance
    subset_instance = SubsetSumInstance(numbers, target)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="SubsetSum",
        size=set_size,
        parameters={
            "set_size": set_size,
            "max_value": max_value,
            "target": target,
            "seed": seed
        },
        data=subset_instance,
        metadata={
            "total_sum": sum(numbers),
            "average_value": sum(numbers) / len(numbers),
            "min_value": min(numbers),
            "max_value_actual": max(numbers),
            "generation_method": "random_subset_sum"
        }
    )
    
    return problem_instance


def generate_solvable_subset_sum_instance(set_size: int, max_value: int = None, seed: int = None) -> ProblemInstance:
    """
    Generate a guaranteed solvable Subset Sum problem instance.
    
    Creates a Subset Sum instance that is guaranteed to have a solution by first
    generating the numbers, then selecting a random subset and using its sum as the target.
    
    Args:
        set_size: Number of integers in the set (must be >= 1)
        max_value: Maximum value for generated integers (defaults to set_size * 10)
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated solvable Subset Sum data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if set_size < 1:
        raise ValueError("Set size must be at least 1")
    if max_value is not None and max_value < 1:
        raise ValueError("Maximum value must be at least 1")
    
    # Set default max_value if not provided
    if max_value is None:
        max_value = set_size * 10
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate random positive integers
    numbers = [random.randint(1, max_value) for _ in range(set_size)]
    
    # Select a random subset and use its sum as the target
    subset_size = random.randint(1, set_size)
    subset_indices = random.sample(range(set_size), subset_size)
    target = sum(numbers[i] for i in subset_indices)
    solution_subset = [numbers[i] for i in subset_indices]
    
    # Create the Subset Sum instance
    subset_instance = SubsetSumInstance(numbers, target)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="SubsetSum",
        size=set_size,
        parameters={
            "set_size": set_size,
            "max_value": max_value,
            "target": target,
            "seed": seed,
            "guaranteed_solvable": True
        },
        data=subset_instance,
        metadata={
            "total_sum": sum(numbers),
            "average_value": sum(numbers) / len(numbers),
            "min_value": min(numbers),
            "max_value_actual": max(numbers),
            "generation_method": "solvable_subset_sum",
            "solution_subset": solution_subset,
            "solution_indices": subset_indices
        }
    )
    
    return problem_instance


def generate_structured_subset_sum_instance(set_size: int, structure_type: str = "arithmetic", seed: int = None) -> ProblemInstance:
    """
    Generate a structured Subset Sum problem instance.
    
    Creates a Subset Sum instance with a specific structure rather than random numbers.
    This can be useful for educational purposes or testing specific algorithmic behaviors.
    
    Args:
        set_size: Number of integers in the set (must be >= 1)
        structure_type: Type of structure ("arithmetic", "geometric", "powers_of_2")
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated structured Subset Sum data
    
    Raises:
        ValueError: If parameters are invalid or structure_type is unknown
    """
    # Validate input parameters
    if set_size < 1:
        raise ValueError("Set size must be at least 1")
    
    valid_structures = ["arithmetic", "geometric", "powers_of_2"]
    if structure_type not in valid_structures:
        raise ValueError(f"Unknown structure type '{structure_type}'. Valid types: {valid_structures}")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate structured numbers based on type
    if structure_type == "arithmetic":
        # Arithmetic progression: start, start+d, start+2d, ...
        start = random.randint(1, 10)
        diff = random.randint(1, 5)
        numbers = [start + i * diff for i in range(set_size)]
    
    elif structure_type == "geometric":
        # Geometric progression: start, start*r, start*r^2, ...
        start = random.randint(1, 5)
        ratio = random.randint(2, 3)  # Keep ratio small to avoid huge numbers
        numbers = [start * (ratio ** i) for i in range(set_size)]
    
    elif structure_type == "powers_of_2":
        # Powers of 2: 1, 2, 4, 8, 16, ...
        numbers = [2 ** i for i in range(set_size)]
    
    # Generate a target by selecting a random subset
    subset_size = random.randint(1, min(set_size, 4))  # Limit subset size for reasonable targets
    subset_indices = random.sample(range(set_size), subset_size)
    target = sum(numbers[i] for i in subset_indices)
    solution_subset = [numbers[i] for i in subset_indices]
    
    # Create the Subset Sum instance
    subset_instance = SubsetSumInstance(numbers, target)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="SubsetSum",
        size=set_size,
        parameters={
            "set_size": set_size,
            "structure_type": structure_type,
            "target": target,
            "seed": seed
        },
        data=subset_instance,
        metadata={
            "total_sum": sum(numbers),
            "average_value": sum(numbers) / len(numbers),
            "min_value": min(numbers),
            "max_value_actual": max(numbers),
            "generation_method": f"structured_{structure_type}",
            "solution_subset": solution_subset,
            "solution_indices": subset_indices
        }
    )
    
    return problem_instance


# Default parameter configurations for common use cases
DEFAULT_CONFIGS = {
    "small": {"set_size": 5, "max_value": 20},
    "medium": {"set_size": 10, "max_value": 50},
    "large": {"set_size": 15, "max_value": 100},
    "extra_large": {"set_size": 20, "max_value": 200}
}


def get_default_config(size: str) -> Dict[str, int]:
    """
    Get default configuration parameters for common problem sizes.
    
    Args:
        size: Size category ("small", "medium", "large", "extra_large")
    
    Returns:
        Dict containing set_size and max_value for the specified size
    
    Raises:
        ValueError: If the size category is not recognized
    """
    if size not in DEFAULT_CONFIGS:
        available_sizes = ", ".join(DEFAULT_CONFIGS.keys())
        raise ValueError(f"Unknown size '{size}'. Available sizes: {available_sizes}")
    
    return DEFAULT_CONFIGS[size].copy()