"""
SAT solver implementations.

This module provides different algorithms for solving the Boolean Satisfiability (SAT) problem,
including brute-force and optimized approaches for educational and benchmarking purposes.
"""

from typing import List, Optional, Dict, Tuple
from core.base_solver import BaseSolver
from generators.sat_generator import SATInstance


class SATBruteForceSolver(BaseSolver):
    """
    Brute-force SAT solver using exhaustive truth table evaluation.
    
    This solver tries all possible truth assignments for the variables
    and checks if any assignment satisfies all clauses. The time complexity
    is O(2^n * m) where n is the number of variables and m is the number of clauses.
    """
    
    def solve(self, problem_instance: SATInstance) -> Dict:
        """
        Solve the SAT instance using brute-force approach.
        
        Args:
            problem_instance: A SATInstance containing the clauses to satisfy
        
        Returns:
            Dict containing:
                - 'satisfiable': bool indicating if the instance is satisfiable
                - 'assignment': List[bool] with the satisfying assignment (if found)
                - 'assignments_tried': int number of assignments evaluated
        """
        if not isinstance(problem_instance, SATInstance):
            raise TypeError("Expected SATInstance, got {}".format(type(problem_instance)))
        
        num_variables = problem_instance.num_variables
        clauses = problem_instance.clauses
        assignments_tried = 0
        
        # Try all possible truth assignments (2^n possibilities)
        for assignment_int in range(2 ** num_variables):
            assignments_tried += 1
            
            # Convert integer to binary assignment
            # assignment_int = 0 -> [False, False, ..., False]
            # assignment_int = 1 -> [False, False, ..., True]
            # etc.
            assignment = []
            temp = assignment_int
            for _ in range(num_variables):
                assignment.append(bool(temp & 1))
                temp >>= 1
            
            # Check if this assignment satisfies all clauses
            if self._evaluate_assignment(assignment, clauses):
                return {
                    'satisfiable': True,
                    'assignment': assignment,
                    'assignments_tried': assignments_tried
                }
        
        # No satisfying assignment found
        return {
            'satisfiable': False,
            'assignment': None,
            'assignments_tried': assignments_tried
        }
    
    def _evaluate_assignment(self, assignment: List[bool], clauses: List[List[int]]) -> bool:
        """
        Evaluate whether a truth assignment satisfies all clauses.
        
        Args:
            assignment: List of boolean values for variables (indexed from 0)
            clauses: List of clauses, each containing literals
        
        Returns:
            bool: True if all clauses are satisfied, False otherwise
        """
        for clause in clauses:
            clause_satisfied = False
            
            # Check each literal in the clause
            for literal in clause:
                variable_index = abs(literal) - 1  # Convert to 0-based index
                variable_value = assignment[variable_index]
                
                if literal > 0:
                    # Positive literal: satisfied if variable is True
                    if variable_value:
                        clause_satisfied = True
                        break
                else:
                    # Negative literal: satisfied if variable is False
                    if not variable_value:
                        clause_satisfied = True
                        break
            
            # If any clause is not satisfied, the entire formula is not satisfied
            if not clause_satisfied:
                return False
        
        # All clauses are satisfied
        return True
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "NP-Complete (Exponential Time)"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Brute Force SAT Solver"


class SATResult:
    """
    Container for SAT solver results with additional utility methods.
    """
    
    def __init__(self, satisfiable: bool, assignment: Optional[List[bool]] = None, 
                 assignments_tried: int = 0, additional_info: Dict = None):
        """
        Initialize SAT result.
        
        Args:
            satisfiable: Whether the instance is satisfiable
            assignment: Satisfying assignment if found
            assignments_tried: Number of assignments evaluated
            additional_info: Additional solver-specific information
        """
        self.satisfiable = satisfiable
        self.assignment = assignment
        self.assignments_tried = assignments_tried
        self.additional_info = additional_info or {}
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        if self.satisfiable:
            assignment_str = ", ".join(
                f"x{i+1}={assignment}" 
                for i, assignment in enumerate(self.assignment)
            )
            return f"SATISFIABLE: {assignment_str} (tried {self.assignments_tried} assignments)"
        else:
            return f"UNSATISFIABLE (tried {self.assignments_tried} assignments)"
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        result = {
            'satisfiable': self.satisfiable,
            'assignment': self.assignment,
            'assignments_tried': self.assignments_tried
        }
        result.update(self.additional_info)
        return result


class SATOptimizedSolver(BaseSolver):
    """
    Optimized SAT solver using DPLL-style algorithm.
    
    This solver implements the Davis-Putnam-Logemann-Loveland (DPLL) algorithm
    with unit propagation and pure literal elimination. While still exponential
    in the worst case, it performs much better than brute force on many instances.
    """
    
    def solve(self, problem_instance: SATInstance) -> Dict:
        """
        Solve the SAT instance using DPLL algorithm.
        
        Args:
            problem_instance: A SATInstance containing the clauses to satisfy
        
        Returns:
            Dict containing:
                - 'satisfiable': bool indicating if the instance is satisfiable
                - 'assignment': List[bool] with the satisfying assignment (if found)
                - 'assignments_tried': int number of assignments evaluated
                - 'unit_propagations': int number of unit propagations performed
                - 'pure_eliminations': int number of pure literal eliminations
        """
        if not isinstance(problem_instance, SATInstance):
            raise TypeError("Expected SATInstance, got {}".format(type(problem_instance)))
        
        self.assignments_tried = 0
        self.unit_propagations = 0
        self.pure_eliminations = 0
        
        # Convert clauses to a more convenient format for DPLL
        clauses = [clause[:] for clause in problem_instance.clauses]  # Deep copy
        assignment = [None] * problem_instance.num_variables  # None = unassigned
        
        result = self._dpll(clauses, assignment)
        
        if result:
            return {
                'satisfiable': True,
                'assignment': [bool(val) for val in assignment],
                'assignments_tried': self.assignments_tried,
                'unit_propagations': self.unit_propagations,
                'pure_eliminations': self.pure_eliminations
            }
        else:
            return {
                'satisfiable': False,
                'assignment': None,
                'assignments_tried': self.assignments_tried,
                'unit_propagations': self.unit_propagations,
                'pure_eliminations': self.pure_eliminations
            }
    
    def _dpll(self, clauses: List[List[int]], assignment: List[Optional[bool]]) -> bool:
        """
        Recursive DPLL algorithm implementation.
        
        Args:
            clauses: Current set of clauses (modified during recursion)
            assignment: Current partial assignment
        
        Returns:
            bool: True if satisfiable, False otherwise
        """
        # Remove satisfied clauses and simplify remaining clauses
        clauses = self._simplify_clauses(clauses, assignment)
        
        # Check for empty clause (unsatisfiable)
        if any(len(clause) == 0 for clause in clauses):
            return False
        
        # Check if all clauses are satisfied
        if len(clauses) == 0:
            return True
        
        # Unit propagation
        unit_literal = self._find_unit_literal(clauses)
        if unit_literal is not None:
            self.unit_propagations += 1
            var_index = abs(unit_literal) - 1
            assignment[var_index] = unit_literal > 0
            return self._dpll(clauses, assignment)
        
        # Pure literal elimination
        pure_literal = self._find_pure_literal(clauses)
        if pure_literal is not None:
            self.pure_eliminations += 1
            var_index = abs(pure_literal) - 1
            assignment[var_index] = pure_literal > 0
            return self._dpll(clauses, assignment)
        
        # Choose a variable to branch on (first unassigned variable)
        branch_var = self._choose_branch_variable(assignment)
        if branch_var is None:
            return True  # All variables assigned and no conflicts
        
        # Try positive assignment first
        self.assignments_tried += 1
        assignment_copy = assignment[:]
        assignment_copy[branch_var - 1] = True
        if self._dpll(clauses, assignment_copy):
            # Copy successful assignment back
            assignment[:] = assignment_copy
            return True
        
        # Try negative assignment
        self.assignments_tried += 1
        assignment_copy = assignment[:]
        assignment_copy[branch_var - 1] = False
        if self._dpll(clauses, assignment_copy):
            # Copy successful assignment back
            assignment[:] = assignment_copy
            return True
        
        return False
    
    def _simplify_clauses(self, clauses: List[List[int]], assignment: List[Optional[bool]]) -> List[List[int]]:
        """
        Simplify clauses based on current assignment.
        
        Args:
            clauses: List of clauses to simplify
            assignment: Current variable assignment
        
        Returns:
            List of simplified clauses
        """
        simplified = []
        
        for clause in clauses:
            new_clause = []
            clause_satisfied = False
            
            for literal in clause:
                var_index = abs(literal) - 1
                var_value = assignment[var_index]
                
                if var_value is None:
                    # Variable not assigned yet, keep literal
                    new_clause.append(literal)
                elif (literal > 0 and var_value) or (literal < 0 and not var_value):
                    # Literal is satisfied, entire clause is satisfied
                    clause_satisfied = True
                    break
                # If literal is false, don't add it to new_clause
            
            if not clause_satisfied:
                simplified.append(new_clause)
        
        return simplified
    
    def _find_unit_literal(self, clauses: List[List[int]]) -> Optional[int]:
        """
        Find a unit literal (clause with only one unassigned literal).
        
        Args:
            clauses: List of clauses to search
        
        Returns:
            The unit literal if found, None otherwise
        """
        for clause in clauses:
            if len(clause) == 1:
                return clause[0]
        return None
    
    def _find_pure_literal(self, clauses: List[List[int]]) -> Optional[int]:
        """
        Find a pure literal (variable that appears only in positive or only in negative form).
        
        Args:
            clauses: List of clauses to search
        
        Returns:
            A pure literal if found, None otherwise
        """
        literal_occurrences = set()
        
        # Collect all literals that appear
        for clause in clauses:
            for literal in clause:
                literal_occurrences.add(literal)
        
        # Find variables that appear only in one polarity
        variables_checked = set()
        for literal in literal_occurrences:
            var = abs(literal)
            if var in variables_checked:
                continue
            
            variables_checked.add(var)
            
            # Check if both positive and negative forms exist
            has_positive = var in literal_occurrences
            has_negative = -var in literal_occurrences
            
            if has_positive and not has_negative:
                return var  # Return positive literal
            elif has_negative and not has_positive:
                return -var  # Return negative literal
        
        return None
    
    def _choose_branch_variable(self, assignment: List[Optional[bool]]) -> Optional[int]:
        """
        Choose the next variable to branch on.
        
        Args:
            assignment: Current assignment
        
        Returns:
            Variable number (1-indexed) to branch on, or None if all assigned
        """
        for i, value in enumerate(assignment):
            if value is None:
                return i + 1  # Return 1-indexed variable number
        return None
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "NP-Complete (Exponential Time - Optimized)"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "DPLL SAT Solver"


def verify_sat_solution(sat_instance: SATInstance, assignment: List[bool]) -> bool:
    """
    Verify that a given assignment satisfies a SAT instance.
    
    This is a utility function that can be used to verify solutions
    from any SAT solver implementation.
    
    Args:
        sat_instance: The SAT instance to verify against
        assignment: The truth assignment to verify
    
    Returns:
        bool: True if the assignment satisfies all clauses, False otherwise
    
    Raises:
        ValueError: If assignment length doesn't match number of variables
    """
    if len(assignment) != sat_instance.num_variables:
        raise ValueError(
            f"Assignment length ({len(assignment)}) doesn't match "
            f"number of variables ({sat_instance.num_variables})"
        )
    
    for clause in sat_instance.clauses:
        clause_satisfied = False
        
        for literal in clause:
            variable_index = abs(literal) - 1
            variable_value = assignment[variable_index]
            
            if literal > 0:
                # Positive literal
                if variable_value:
                    clause_satisfied = True
                    break
            else:
                # Negative literal
                if not variable_value:
                    clause_satisfied = True
                    break
        
        if not clause_satisfied:
            return False
    
    return True