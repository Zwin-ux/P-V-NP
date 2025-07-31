"""
Subset Sum solver implementations.

This module provides different algorithms for solving the Subset Sum problem,
including brute-force and optimized approaches for educational and benchmarking purposes.
"""

from typing import List, Optional, Dict, Set, Tuple
from core.base_solver import BaseSolver
from generators.subset_generator import SubsetSumInstance


class SubsetSumBruteForce(BaseSolver):
    """
    Brute-force Subset Sum solver using exhaustive subset enumeration.
    
    This solver tries all possible subsets of the given numbers and checks
    if any subset sums to the target value. The time complexity is O(2^n)
    where n is the number of elements in the set.
    """
    
    def solve(self, problem_instance: SubsetSumInstance) -> Dict:
        """
        Solve the Subset Sum instance using brute-force approach.
        
        Args:
            problem_instance: A SubsetSumInstance containing numbers and target
        
        Returns:
            Dict containing:
                - 'solution_found': bool indicating if a solution exists
                - 'solution_subset': List[int] with the subset that sums to target (if found)
                - 'solution_indices': List[int] with indices of solution elements (if found)
                - 'subsets_tried': int number of subsets evaluated
                - 'target': int the target sum
        """
        if not isinstance(problem_instance, SubsetSumInstance):
            raise TypeError("Expected SubsetSumInstance, got {}".format(type(problem_instance)))
        
        numbers = problem_instance.numbers
        target = problem_instance.target
        n = len(numbers)
        subsets_tried = 0
        
        # Try all possible subsets (2^n possibilities)
        # Use bit manipulation: each integer from 0 to 2^n-1 represents a subset
        for subset_mask in range(2 ** n):
            subsets_tried += 1
            
            # Extract subset based on bit mask
            current_subset = []
            current_indices = []
            current_sum = 0
            
            for i in range(n):
                if subset_mask & (1 << i):  # Check if i-th bit is set
                    current_subset.append(numbers[i])
                    current_indices.append(i)
                    current_sum += numbers[i]
            
            # Check if this subset sums to the target
            if current_sum == target:
                return {
                    'solution_found': True,
                    'solution_subset': current_subset,
                    'solution_indices': current_indices,
                    'subsets_tried': subsets_tried,
                    'target': target
                }
        
        # No solution found
        return {
            'solution_found': False,
            'solution_subset': None,
            'solution_indices': None,
            'subsets_tried': subsets_tried,
            'target': target
        }
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "NP-Complete (Exponential Time)"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Brute Force Subset Sum Solver"


class SubsetSumResult:
    """
    Container for Subset Sum solver results with additional utility methods.
    """
    
    def __init__(self, solution_found: bool, solution_subset: Optional[List[int]] = None,
                 solution_indices: Optional[List[int]] = None, subsets_tried: int = 0,
                 target: int = 0, additional_info: Dict = None):
        """
        Initialize Subset Sum result.
        
        Args:
            solution_found: Whether a solution was found
            solution_subset: The subset that sums to target (if found)
            solution_indices: Indices of solution elements (if found)
            subsets_tried: Number of subsets evaluated
            target: The target sum
            additional_info: Additional solver-specific information
        """
        self.solution_found = solution_found
        self.solution_subset = solution_subset or []
        self.solution_indices = solution_indices or []
        self.subsets_tried = subsets_tried
        self.target = target
        self.additional_info = additional_info or {}
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        if self.solution_found:
            subset_str = "{" + ", ".join(map(str, self.solution_subset)) + "}"
            sum_value = sum(self.solution_subset)
            return f"SOLUTION FOUND: {subset_str} = {sum_value} (tried {self.subsets_tried} subsets)"
        else:
            return f"NO SOLUTION (tried {self.subsets_tried} subsets)"
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        result = {
            'solution_found': self.solution_found,
            'solution_subset': self.solution_subset,
            'solution_indices': self.solution_indices,
            'subsets_tried': self.subsets_tried,
            'target': self.target
        }
        result.update(self.additional_info)
        return result


def verify_subset_sum_solution(subset_instance: SubsetSumInstance, 
                              solution_subset: List[int]) -> bool:
    """
    Verify that a given subset is a valid solution to a Subset Sum instance.
    
    This is a utility function that can be used to verify solutions
    from any Subset Sum solver implementation.
    
    Args:
        subset_instance: The Subset Sum instance to verify against
        solution_subset: The subset to verify
    
    Returns:
        bool: True if the subset sums to the target, False otherwise
    
    Raises:
        ValueError: If solution contains elements not in the original set
    """
    # Check that all elements in solution are from the original set
    original_numbers = subset_instance.numbers
    for element in solution_subset:
        if element not in original_numbers:
            raise ValueError(f"Solution contains element {element} not in original set")
    
    # Check that the subset sums to the target
    return sum(solution_subset) == subset_instance.target


class SubsetSumDP(BaseSolver):
    """
    Optimized Subset Sum solver using dynamic programming.
    
    This solver uses a dynamic programming approach with a 2D table to determine
    if a subset sum is possible. The time complexity is O(n * sum) where n is
    the number of elements and sum is the target value. Space complexity is also
    O(n * sum), but can be optimized to O(sum) with careful implementation.
    """
    
    def solve(self, problem_instance: SubsetSumInstance) -> Dict:
        """
        Solve the Subset Sum instance using dynamic programming approach.
        
        Args:
            problem_instance: A SubsetSumInstance containing numbers and target
        
        Returns:
            Dict containing:
                - 'solution_found': bool indicating if a solution exists
                - 'solution_subset': List[int] with the subset that sums to target (if found)
                - 'solution_indices': List[int] with indices of solution elements (if found)
                - 'dp_table_size': int size of the DP table used
                - 'target': int the target sum
        """
        if not isinstance(problem_instance, SubsetSumInstance):
            raise TypeError("Expected SubsetSumInstance, got {}".format(type(problem_instance)))
        
        numbers = problem_instance.numbers
        target = problem_instance.target
        n = len(numbers)
        
        # Handle edge cases
        if target == 0:
            return {
                'solution_found': True,
                'solution_subset': [],
                'solution_indices': [],
                'dp_table_size': 0,
                'target': target
            }
        
        if target < 0:
            return {
                'solution_found': False,
                'solution_subset': None,
                'solution_indices': None,
                'dp_table_size': 0,
                'target': target
            }
        
        # Create DP table: dp[i][j] = True if subset of first i elements can sum to j
        # We use (n+1) x (target+1) table for easier indexing
        dp = [[False for _ in range(target + 1)] for _ in range(n + 1)]
        
        # Base case: empty subset sums to 0
        for i in range(n + 1):
            dp[i][0] = True
        
        # Fill the DP table
        for i in range(1, n + 1):
            for j in range(1, target + 1):
                # Option 1: Don't include current element
                dp[i][j] = dp[i-1][j]
                
                # Option 2: Include current element (if it doesn't exceed target)
                if numbers[i-1] <= j:
                    dp[i][j] = dp[i][j] or dp[i-1][j - numbers[i-1]]
        
        # Check if solution exists
        if not dp[n][target]:
            return {
                'solution_found': False,
                'solution_subset': None,
                'solution_indices': None,
                'dp_table_size': (n + 1) * (target + 1),
                'target': target
            }
        
        # Reconstruct the solution by backtracking through the DP table
        solution_subset = []
        solution_indices = []
        i, j = n, target
        
        while i > 0 and j > 0:
            # If dp[i][j] is True but dp[i-1][j] is False,
            # then the i-th element must be included
            if dp[i][j] and not dp[i-1][j]:
                solution_subset.append(numbers[i-1])
                solution_indices.append(i-1)
                j -= numbers[i-1]
            i -= 1
        
        # Reverse to get elements in original order
        solution_subset.reverse()
        solution_indices.reverse()
        
        return {
            'solution_found': True,
            'solution_subset': solution_subset,
            'solution_indices': solution_indices,
            'dp_table_size': (n + 1) * (target + 1),
            'target': target
        }
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "Pseudo-polynomial Time (O(n * sum))"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Dynamic Programming Subset Sum Solver"


def find_all_subset_sum_solutions(subset_instance: SubsetSumInstance) -> List[List[int]]:
    """
    Find all possible solutions to a Subset Sum instance.
    
    This function finds all subsets that sum to the target value,
    not just the first one found.
    
    Args:
        subset_instance: The Subset Sum instance to solve
    
    Returns:
        List of all solution subsets (each subset is a List[int])
    """
    numbers = subset_instance.numbers
    target = subset_instance.target
    n = len(numbers)
    all_solutions = []
    
    # Try all possible subsets
    for subset_mask in range(2 ** n):
        current_subset = []
        current_sum = 0
        
        for i in range(n):
            if subset_mask & (1 << i):
                current_subset.append(numbers[i])
                current_sum += numbers[i]
        
        if current_sum == target:
            all_solutions.append(current_subset)
    
    return all_solutions