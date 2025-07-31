"""
Unit tests for the data model classes.

This module tests the data model classes (ProblemInstance, BenchmarkResult,
AlgorithmConfig) to ensure they work correctly and maintain data integrity.
"""

import unittest
from datetime import datetime
from typing import Dict, Any
from core.data_models import ProblemInstance, BenchmarkResult, AlgorithmConfig
from core.base_solver import BaseSolver


class MockSolver(BaseSolver):
    """Mock solver for testing AlgorithmConfig."""
    
    def solve(self, problem_instance):
        return "mock_solution"
    
    def get_complexity_class(self):
        return "NP"
    
    def get_algorithm_name(self):
        return "Mock Solver"


class TestProblemInstance(unittest.TestCase):
    """Test cases for the ProblemInstance data class."""
    
    def test_problem_instance_creation(self):
        """Test that ProblemInstance can be created with all required fields."""
        instance = ProblemInstance(
            problem_type="SAT",
            size=10,
            parameters={"variables": 10, "clauses": 30},
            data=[[1, -2, 3], [-1, 2, -3]],
            metadata={"generator": "random", "seed": 42}
        )
        
        self.assertEqual(instance.problem_type, "SAT")
        self.assertEqual(instance.size, 10)
        self.assertEqual(instance.parameters["variables"], 10)
        self.assertEqual(instance.parameters["clauses"], 30)
        self.assertEqual(len(instance.data), 2)
        self.assertEqual(instance.metadata["generator"], "random")
        self.assertEqual(instance.metadata["seed"], 42)
    
    def test_problem_instance_equality(self):
        """Test that ProblemInstance instances can be compared for equality."""
        instance1 = ProblemInstance(
            problem_type="TSP",
            size=5,
            parameters={"cities": 5},
            data=[[0, 1, 2], [1, 0, 3], [2, 3, 0]],
            metadata={"type": "symmetric"}
        )
        
        instance2 = ProblemInstance(
            problem_type="TSP",
            size=5,
            parameters={"cities": 5},
            data=[[0, 1, 2], [1, 0, 3], [2, 3, 0]],
            metadata={"type": "symmetric"}
        )
        
        self.assertEqual(instance1, instance2)
    
    def test_problem_instance_different_data(self):
        """Test that ProblemInstance instances with different data are not equal."""
        instance1 = ProblemInstance(
            problem_type="SubsetSum",
            size=5,
            parameters={"target": 10},
            data=[1, 2, 3, 4, 5],
            metadata={}
        )
        
        instance2 = ProblemInstance(
            problem_type="SubsetSum",
            size=5,
            parameters={"target": 10},
            data=[1, 2, 3, 4, 6],  # Different data
            metadata={}
        )
        
        self.assertNotEqual(instance1, instance2)


class TestBenchmarkResult(unittest.TestCase):
    """Test cases for the BenchmarkResult data class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.problem_instance = ProblemInstance(
            problem_type="SAT",
            size=5,
            parameters={"variables": 5, "clauses": 10},
            data=[[1, -2, 3]],
            metadata={}
        )
        self.timestamp = datetime.now()
    
    def test_benchmark_result_creation(self):
        """Test that BenchmarkResult can be created with all required fields."""
        result = BenchmarkResult(
            algorithm_name="Brute Force SAT",
            problem_instance=self.problem_instance,
            execution_time=1.234,
            solution_found=True,
            solution_data={"assignment": [True, False, True, False, True]},
            timeout_occurred=False,
            memory_usage=15.6,
            timestamp=self.timestamp
        )
        
        self.assertEqual(result.algorithm_name, "Brute Force SAT")
        self.assertEqual(result.problem_instance, self.problem_instance)
        self.assertEqual(result.execution_time, 1.234)
        self.assertTrue(result.solution_found)
        self.assertEqual(result.solution_data["assignment"][0], True)
        self.assertFalse(result.timeout_occurred)
        self.assertEqual(result.memory_usage, 15.6)
        self.assertEqual(result.timestamp, self.timestamp)
    
    def test_benchmark_result_with_timeout(self):
        """Test BenchmarkResult creation when timeout occurred."""
        result = BenchmarkResult(
            algorithm_name="Slow Algorithm",
            problem_instance=self.problem_instance,
            execution_time=30.0,
            solution_found=False,
            solution_data=None,
            timeout_occurred=True,
            memory_usage=None,
            timestamp=self.timestamp
        )
        
        self.assertTrue(result.timeout_occurred)
        self.assertFalse(result.solution_found)
        self.assertIsNone(result.solution_data)
        self.assertIsNone(result.memory_usage)
    
    def test_benchmark_result_no_solution(self):
        """Test BenchmarkResult when no solution exists (unsatisfiable problem)."""
        result = BenchmarkResult(
            algorithm_name="SAT Solver",
            problem_instance=self.problem_instance,
            execution_time=0.5,
            solution_found=False,
            solution_data=None,
            timeout_occurred=False,
            memory_usage=8.2,
            timestamp=self.timestamp
        )
        
        self.assertFalse(result.solution_found)
        self.assertFalse(result.timeout_occurred)
        self.assertIsNone(result.solution_data)
        self.assertEqual(result.memory_usage, 8.2)


class TestAlgorithmConfig(unittest.TestCase):
    """Test cases for the AlgorithmConfig data class."""
    
    def test_algorithm_config_creation(self):
        """Test that AlgorithmConfig can be created with all required fields."""
        config = AlgorithmConfig(
            name="Mock Algorithm",
            solver_class=MockSolver,
            timeout_seconds=60,
            parameters={"max_iterations": 1000, "use_heuristic": True}
        )
        
        self.assertEqual(config.name, "Mock Algorithm")
        self.assertEqual(config.solver_class, MockSolver)
        self.assertEqual(config.timeout_seconds, 60)
        self.assertEqual(config.parameters["max_iterations"], 1000)
        self.assertTrue(config.parameters["use_heuristic"])
    
    def test_algorithm_config_solver_instantiation(self):
        """Test that the solver class can be instantiated from the config."""
        config = AlgorithmConfig(
            name="Test Config",
            solver_class=MockSolver,
            timeout_seconds=30,
            parameters={}
        )
        
        # Test that we can create an instance of the solver
        solver_instance = config.solver_class()
        self.assertIsInstance(solver_instance, MockSolver)
        self.assertIsInstance(solver_instance, BaseSolver)
        
        # Test that the solver methods work
        self.assertEqual(solver_instance.get_algorithm_name(), "Mock Solver")
        self.assertEqual(solver_instance.get_complexity_class(), "NP")
        self.assertEqual(solver_instance.solve("test"), "mock_solution")
    
    def test_algorithm_config_equality(self):
        """Test that AlgorithmConfig instances can be compared for equality."""
        config1 = AlgorithmConfig(
            name="Config A",
            solver_class=MockSolver,
            timeout_seconds=45,
            parameters={"param1": "value1"}
        )
        
        config2 = AlgorithmConfig(
            name="Config A",
            solver_class=MockSolver,
            timeout_seconds=45,
            parameters={"param1": "value1"}
        )
        
        self.assertEqual(config1, config2)
    
    def test_algorithm_config_different_parameters(self):
        """Test that AlgorithmConfig instances with different parameters are not equal."""
        config1 = AlgorithmConfig(
            name="Config A",
            solver_class=MockSolver,
            timeout_seconds=30,
            parameters={"param1": "value1"}
        )
        
        config2 = AlgorithmConfig(
            name="Config A",
            solver_class=MockSolver,
            timeout_seconds=30,
            parameters={"param1": "value2"}  # Different parameter value
        )
        
        self.assertNotEqual(config1, config2)


if __name__ == '__main__':
    unittest.main()