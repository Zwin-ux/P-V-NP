"""
Unit tests for the BaseSolver abstract base class.

This module tests the interface contract and behavior of the BaseSolver
abstract base class to ensure proper inheritance and method implementation.
"""

import unittest
from abc import ABC
from core.base_solver import BaseSolver


class ConcreteSolver(BaseSolver):
    """Concrete implementation of BaseSolver for testing purposes."""
    
    def solve(self, problem_instance):
        return f"Solved: {problem_instance}"
    
    def get_complexity_class(self):
        return "P"
    
    def get_algorithm_name(self):
        return "Test Solver"


class IncompleteSolver(BaseSolver):
    """Incomplete implementation missing required methods."""
    pass


class TestBaseSolver(unittest.TestCase):
    """Test cases for the BaseSolver abstract base class."""
    
    def test_base_solver_is_abstract(self):
        """Test that BaseSolver cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseSolver()
    
    def test_concrete_solver_can_be_instantiated(self):
        """Test that a complete concrete implementation can be instantiated."""
        solver = ConcreteSolver()
        self.assertIsInstance(solver, BaseSolver)
        self.assertIsInstance(solver, ConcreteSolver)
    
    def test_incomplete_solver_cannot_be_instantiated(self):
        """Test that incomplete implementations cannot be instantiated."""
        with self.assertRaises(TypeError):
            IncompleteSolver()
    
    def test_concrete_solver_methods(self):
        """Test that concrete solver methods work as expected."""
        solver = ConcreteSolver()
        
        # Test solve method
        result = solver.solve("test_problem")
        self.assertEqual(result, "Solved: test_problem")
        
        # Test get_complexity_class method
        complexity = solver.get_complexity_class()
        self.assertEqual(complexity, "P")
        
        # Test get_algorithm_name method
        name = solver.get_algorithm_name()
        self.assertEqual(name, "Test Solver")
    
    def test_base_solver_inheritance(self):
        """Test that BaseSolver properly inherits from ABC."""
        self.assertTrue(issubclass(BaseSolver, ABC))
        
        # Test that concrete solver is instance of both BaseSolver and ABC
        solver = ConcreteSolver()
        self.assertIsInstance(solver, BaseSolver)
        self.assertIsInstance(solver, ABC)


if __name__ == '__main__':
    unittest.main()