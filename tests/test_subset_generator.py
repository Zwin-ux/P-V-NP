"""
Unit tests for the Subset Sum problem generator.

This module contains comprehensive tests for the subset sum instance generation
functionality, including parameter validation, reproducibility, and correctness.
"""

import unittest
import random
from generators.subset_generator import (
    SubsetSumInstance,
    generate_subset_sum_instance,
    generate_solvable_subset_sum_instance,
    generate_structured_subset_sum_instance,
    get_default_config,
    DEFAULT_CONFIGS
)
from core.data_models import ProblemInstance


class TestSubsetSumInstance(unittest.TestCase):
    """Test cases for the SubsetSumInstance class."""
    
    def test_init(self):
        """Test SubsetSumInstance initialization."""
        numbers = [1, 2, 3, 4, 5]
        target = 7
        instance = SubsetSumInstance(numbers, target)
        
        self.assertEqual(instance.numbers, numbers)
        self.assertEqual(instance.target, target)
    
    def test_str_representation(self):
        """Test string representation of SubsetSumInstance."""
        numbers = [1, 2, 3]
        target = 5
        instance = SubsetSumInstance(numbers, target)
        
        str_repr = str(instance)
        self.assertIn("3 numbers", str_repr)
        self.assertIn("target = 5", str_repr)
        self.assertIn("[1, 2, 3]", str_repr)


class TestGenerateSubsetSumInstance(unittest.TestCase):
    """Test cases for generate_subset_sum_instance function."""
    
    def test_basic_generation(self):
        """Test basic subset sum instance generation."""
        problem = generate_subset_sum_instance(5, max_value=10, target=15)
        
        # Check problem instance structure
        self.assertIsInstance(problem, ProblemInstance)
        self.assertEqual(problem.problem_type, "SubsetSum")
        self.assertEqual(problem.size, 5)
        
        # Check data
        self.assertIsInstance(problem.data, SubsetSumInstance)
        self.assertEqual(len(problem.data.numbers), 5)
        self.assertEqual(problem.data.target, 15)
        
        # Check all numbers are within range
        for num in problem.data.numbers:
            self.assertGreaterEqual(num, 1)
            self.assertLessEqual(num, 10)
        
        # Check parameters
        self.assertEqual(problem.parameters["set_size"], 5)
        self.assertEqual(problem.parameters["max_value"], 10)
        self.assertEqual(problem.parameters["target"], 15)
    
    def test_default_max_value(self):
        """Test generation with default max_value."""
        problem = generate_subset_sum_instance(5, target=20)
        
        # Default max_value should be set_size * 10 = 50
        self.assertEqual(problem.parameters["max_value"], 50)
        
        # Check all numbers are within default range
        for num in problem.data.numbers:
            self.assertGreaterEqual(num, 1)
            self.assertLessEqual(num, 50)
    
    def test_random_target_generation(self):
        """Test generation with random target."""
        problem = generate_subset_sum_instance(5, max_value=10)
        
        # Target should be generated automatically
        self.assertIsInstance(problem.data.target, int)
        self.assertGreater(problem.data.target, 0)
        
        # Target should be achievable (sum of some subset)
        total_sum = sum(problem.data.numbers)
        self.assertLessEqual(problem.data.target, total_sum)
    
    def test_reproducibility_with_seed(self):
        """Test that using the same seed produces identical results."""
        problem1 = generate_subset_sum_instance(5, max_value=10, target=15, seed=42)
        problem2 = generate_subset_sum_instance(5, max_value=10, target=15, seed=42)
        
        self.assertEqual(problem1.data.numbers, problem2.data.numbers)
        self.assertEqual(problem1.data.target, problem2.data.target)
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        problem1 = generate_subset_sum_instance(10, max_value=20, seed=1)
        problem2 = generate_subset_sum_instance(10, max_value=20, seed=2)
        
        # Very unlikely to be identical with different seeds
        self.assertNotEqual(problem1.data.numbers, problem2.data.numbers)
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Invalid set_size
        with self.assertRaises(ValueError):
            generate_subset_sum_instance(0)
        
        with self.assertRaises(ValueError):
            generate_subset_sum_instance(-1)
        
        # Invalid max_value
        with self.assertRaises(ValueError):
            generate_subset_sum_instance(5, max_value=0)
        
        with self.assertRaises(ValueError):
            generate_subset_sum_instance(5, max_value=-1)
        
        # Invalid target
        with self.assertRaises(ValueError):
            generate_subset_sum_instance(5, target=-1)
    
    def test_metadata_generation(self):
        """Test that metadata is correctly generated."""
        problem = generate_subset_sum_instance(5, max_value=10, target=15)
        
        metadata = problem.metadata
        self.assertIn("total_sum", metadata)
        self.assertIn("average_value", metadata)
        self.assertIn("min_value", metadata)
        self.assertIn("max_value_actual", metadata)
        self.assertIn("generation_method", metadata)
        
        # Check metadata values
        numbers = problem.data.numbers
        self.assertEqual(metadata["total_sum"], sum(numbers))
        self.assertEqual(metadata["average_value"], sum(numbers) / len(numbers))
        self.assertEqual(metadata["min_value"], min(numbers))
        self.assertEqual(metadata["max_value_actual"], max(numbers))
        self.assertEqual(metadata["generation_method"], "random_subset_sum")


class TestGenerateSolvableSubsetSumInstance(unittest.TestCase):
    """Test cases for generate_solvable_subset_sum_instance function."""
    
    def test_solvable_generation(self):
        """Test that generated instances are guaranteed to be solvable."""
        problem = generate_solvable_subset_sum_instance(5, max_value=10, seed=42)
        
        # Check basic structure
        self.assertIsInstance(problem, ProblemInstance)
        self.assertEqual(problem.problem_type, "SubsetSum")
        self.assertTrue(problem.parameters["guaranteed_solvable"])
        
        # Check that solution metadata exists
        metadata = problem.metadata
        self.assertIn("solution_subset", metadata)
        self.assertIn("solution_indices", metadata)
        
        # Verify the solution is correct
        solution_subset = metadata["solution_subset"]
        self.assertEqual(sum(solution_subset), problem.data.target)
        
        # Verify solution indices are valid
        solution_indices = metadata["solution_indices"]
        numbers = problem.data.numbers
        reconstructed_solution = [numbers[i] for i in solution_indices]
        self.assertEqual(reconstructed_solution, solution_subset)
    
    def test_reproducibility_solvable(self):
        """Test reproducibility of solvable instance generation."""
        problem1 = generate_solvable_subset_sum_instance(5, max_value=10, seed=42)
        problem2 = generate_solvable_subset_sum_instance(5, max_value=10, seed=42)
        
        self.assertEqual(problem1.data.numbers, problem2.data.numbers)
        self.assertEqual(problem1.data.target, problem2.data.target)
        self.assertEqual(problem1.metadata["solution_subset"], problem2.metadata["solution_subset"])


class TestGenerateStructuredSubsetSumInstance(unittest.TestCase):
    """Test cases for generate_structured_subset_sum_instance function."""
    
    def test_arithmetic_structure(self):
        """Test arithmetic progression structure."""
        problem = generate_structured_subset_sum_instance(5, "arithmetic", seed=42)
        
        numbers = problem.data.numbers
        self.assertEqual(len(numbers), 5)
        
        # Check arithmetic progression
        diff = numbers[1] - numbers[0]
        for i in range(1, len(numbers)):
            self.assertEqual(numbers[i] - numbers[i-1], diff)
        
        # Check metadata
        self.assertEqual(problem.metadata["generation_method"], "structured_arithmetic")
        self.assertIn("solution_subset", problem.metadata)
    
    def test_geometric_structure(self):
        """Test geometric progression structure."""
        problem = generate_structured_subset_sum_instance(4, "geometric", seed=42)
        
        numbers = problem.data.numbers
        self.assertEqual(len(numbers), 4)
        
        # Check geometric progression (ratio should be consistent)
        if numbers[0] > 0:  # Avoid division by zero
            ratio = numbers[1] // numbers[0]
            for i in range(1, len(numbers) - 1):
                if numbers[i] > 0:
                    self.assertEqual(numbers[i+1] // numbers[i], ratio)
        
        # Check metadata
        self.assertEqual(problem.metadata["generation_method"], "structured_geometric")
    
    def test_powers_of_2_structure(self):
        """Test powers of 2 structure."""
        problem = generate_structured_subset_sum_instance(5, "powers_of_2", seed=42)
        
        numbers = problem.data.numbers
        expected = [1, 2, 4, 8, 16]
        self.assertEqual(numbers, expected)
        
        # Check metadata
        self.assertEqual(problem.metadata["generation_method"], "structured_powers_of_2")
    
    def test_invalid_structure_type(self):
        """Test invalid structure type."""
        with self.assertRaises(ValueError):
            generate_structured_subset_sum_instance(5, "invalid_structure")
    
    def test_structured_reproducibility(self):
        """Test reproducibility of structured generation."""
        problem1 = generate_structured_subset_sum_instance(5, "arithmetic", seed=42)
        problem2 = generate_structured_subset_sum_instance(5, "arithmetic", seed=42)
        
        self.assertEqual(problem1.data.numbers, problem2.data.numbers)
        self.assertEqual(problem1.data.target, problem2.data.target)


class TestDefaultConfigs(unittest.TestCase):
    """Test cases for default configuration functionality."""
    
    def test_get_default_config_valid_sizes(self):
        """Test getting default configs for valid sizes."""
        for size in DEFAULT_CONFIGS.keys():
            config = get_default_config(size)
            self.assertIn("set_size", config)
            self.assertIn("max_value", config)
            self.assertIsInstance(config["set_size"], int)
            self.assertIsInstance(config["max_value"], int)
            self.assertGreater(config["set_size"], 0)
            self.assertGreater(config["max_value"], 0)
    
    def test_get_default_config_invalid_size(self):
        """Test getting default config for invalid size."""
        with self.assertRaises(ValueError):
            get_default_config("invalid_size")
    
    def test_default_config_independence(self):
        """Test that returned configs are independent copies."""
        config1 = get_default_config("small")
        config2 = get_default_config("small")
        
        # Modify one config
        config1["set_size"] = 999
        
        # Other config should be unchanged
        self.assertNotEqual(config1["set_size"], config2["set_size"])
    
    def test_default_configs_structure(self):
        """Test that default configs have expected structure."""
        self.assertIn("small", DEFAULT_CONFIGS)
        self.assertIn("medium", DEFAULT_CONFIGS)
        self.assertIn("large", DEFAULT_CONFIGS)
        self.assertIn("extra_large", DEFAULT_CONFIGS)
        
        # Check that sizes increase
        small = DEFAULT_CONFIGS["small"]["set_size"]
        medium = DEFAULT_CONFIGS["medium"]["set_size"]
        large = DEFAULT_CONFIGS["large"]["set_size"]
        extra_large = DEFAULT_CONFIGS["extra_large"]["set_size"]
        
        self.assertLess(small, medium)
        self.assertLess(medium, large)
        self.assertLess(large, extra_large)


if __name__ == "__main__":
    unittest.main()