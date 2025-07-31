"""
SAT problem instance generator.

This module provides functionality to generate 3-SAT problem instances
with configurable parameters for educational and benchmarking purposes.
"""

import random
from typing import List, Tuple, Dict, Any
from core.data_models import ProblemInstance


class SATInstance:
    """
    Represents a 3-SAT problem instance.
    
    A 3-SAT instance consists of a set of boolean variables and a set of clauses,
    where each clause contains exactly 3 literals (variables or their negations).
    """
    
    def __init__(self, num_variables: int, clauses: List[List[int]]):
        """
        Initialize a SAT instance.
        
        Args:
            num_variables: Number of boolean variables in the instance
            clauses: List of clauses, where each clause is a list of 3 literals.
                    Positive integers represent variables, negative integers represent negations.
        """
        self.num_variables = num_variables
        self.clauses = clauses
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the SAT instance."""
        result = f"3-SAT instance with {self.num_variables} variables and {len(self.clauses)} clauses:\n"
        for i, clause in enumerate(self.clauses):
            literals = []
            for literal in clause:
                if literal > 0:
                    literals.append(f"x{literal}")
                else:
                    literals.append(f"¬x{abs(literal)}")
            result += f"  Clause {i+1}: ({' ∨ '.join(literals)})\n"
        return result


def generate_3sat_instance(num_variables: int, num_clauses: int, seed: int = None) -> ProblemInstance:
    """
    Generate a random 3-SAT problem instance.
    
    Creates a 3-SAT instance with the specified number of variables and clauses.
    Each clause contains exactly 3 literals, chosen randomly from the available
    variables and their negations.
    
    Args:
        num_variables: Number of boolean variables (must be >= 3)
        num_clauses: Number of clauses to generate (must be >= 1)
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated 3-SAT data
    
    Raises:
        ValueError: If parameters are invalid (num_variables < 3 or num_clauses < 1)
    """
    # Validate input parameters
    if num_variables < 3:
        raise ValueError("Number of variables must be at least 3 for 3-SAT")
    if num_clauses < 1:
        raise ValueError("Number of clauses must be at least 1")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    clauses = []
    
    for _ in range(num_clauses):
        # Generate a clause with 3 distinct literals
        clause = []
        used_variables = set()
        
        while len(clause) < 3:
            # Choose a random variable (1 to num_variables)
            variable = random.randint(1, num_variables)
            
            # Skip if we've already used this variable in this clause
            if variable in used_variables:
                continue
            
            used_variables.add(variable)
            
            # Randomly decide if the literal should be negated
            if random.choice([True, False]):
                clause.append(-variable)  # Negated literal
            else:
                clause.append(variable)   # Positive literal
        
        clauses.append(clause)
    
    # Create the SAT instance
    sat_instance = SATInstance(num_variables, clauses)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="SAT",
        size=num_variables,
        parameters={
            "num_variables": num_variables,
            "num_clauses": num_clauses,
            "seed": seed
        },
        data=sat_instance,
        metadata={
            "clause_to_variable_ratio": num_clauses / num_variables,
            "total_literals": num_clauses * 3,
            "generation_method": "random_3sat"
        }
    )
    
    return problem_instance


def generate_satisfiable_3sat_instance(num_variables: int, num_clauses: int, seed: int = None) -> ProblemInstance:
    """
    Generate a guaranteed satisfiable 3-SAT problem instance.
    
    Creates a 3-SAT instance that is guaranteed to be satisfiable by first
    generating a random truth assignment and then creating clauses that
    are satisfied by that assignment.
    
    Args:
        num_variables: Number of boolean variables (must be >= 3)
        num_clauses: Number of clauses to generate (must be >= 1)
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated satisfiable 3-SAT data
    
    Raises:
        ValueError: If parameters are invalid (num_variables < 3 or num_clauses < 1)
    """
    # Validate input parameters
    if num_variables < 3:
        raise ValueError("Number of variables must be at least 3 for 3-SAT")
    if num_clauses < 1:
        raise ValueError("Number of clauses must be at least 1")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate a random truth assignment
    truth_assignment = [random.choice([True, False]) for _ in range(num_variables)]
    
    clauses = []
    
    for _ in range(num_clauses):
        # Generate a clause that is satisfied by the truth assignment
        clause = []
        used_variables = set()
        
        while len(clause) < 3:
            # Choose a random variable (1 to num_variables)
            variable = random.randint(1, num_variables)
            
            # Skip if we've already used this variable in this clause
            if variable in used_variables:
                continue
            
            used_variables.add(variable)
            
            # Add the literal in a way that makes the clause satisfied
            # If the variable is True in our assignment, add it positively
            # If the variable is False in our assignment, add it negatively
            # But sometimes add it the opposite way to make the problem more interesting
            if random.random() < 0.7:  # 70% chance to follow the satisfying assignment
                if truth_assignment[variable - 1]:  # Variable is True
                    clause.append(variable)  # Add positive literal
                else:  # Variable is False
                    clause.append(-variable)  # Add negative literal
            else:  # 30% chance to add the opposite (still need at least one satisfying literal per clause)
                if truth_assignment[variable - 1]:  # Variable is True
                    clause.append(-variable)  # Add negative literal
                else:  # Variable is False
                    clause.append(variable)  # Add positive literal
        
        # Ensure at least one literal in the clause is satisfied by our truth assignment
        satisfied = any(
            (literal > 0 and truth_assignment[literal - 1]) or
            (literal < 0 and not truth_assignment[abs(literal) - 1])
            for literal in clause
        )
        
        if not satisfied:
            # Replace the first literal with one that satisfies the clause
            var_idx = abs(clause[0]) - 1
            if truth_assignment[var_idx]:
                clause[0] = abs(clause[0])  # Make it positive
            else:
                clause[0] = -abs(clause[0])  # Make it negative
        
        clauses.append(clause)
    
    # Create the SAT instance
    sat_instance = SATInstance(num_variables, clauses)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="SAT",
        size=num_variables,
        parameters={
            "num_variables": num_variables,
            "num_clauses": num_clauses,
            "seed": seed,
            "guaranteed_satisfiable": True
        },
        data=sat_instance,
        metadata={
            "clause_to_variable_ratio": num_clauses / num_variables,
            "total_literals": num_clauses * 3,
            "generation_method": "satisfiable_3sat",
            "satisfying_assignment": truth_assignment
        }
    )
    
    return problem_instance


# Default parameter configurations for common use cases
DEFAULT_CONFIGS = {
    "small": {"num_variables": 5, "num_clauses": 10},
    "medium": {"num_variables": 10, "num_clauses": 25},
    "large": {"num_variables": 15, "num_clauses": 40},
    "extra_large": {"num_variables": 20, "num_clauses": 60}
}


def get_default_config(size: str) -> Dict[str, int]:
    """
    Get default configuration parameters for common problem sizes.
    
    Args:
        size: Size category ("small", "medium", "large", "extra_large")
    
    Returns:
        Dict containing num_variables and num_clauses for the specified size
    
    Raises:
        ValueError: If the size category is not recognized
    """
    if size not in DEFAULT_CONFIGS:
        available_sizes = ", ".join(DEFAULT_CONFIGS.keys())
        raise ValueError(f"Unknown size '{size}'. Available sizes: {available_sizes}")
    
    return DEFAULT_CONFIGS[size].copy()