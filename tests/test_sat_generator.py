"""
Unit tests for the SAT problem generator.

This module contains comprehensive tests for the SAT instance generation
functionality, including parameter validation, output format verification,
and edge case handling.
"""

import unittest
import random
from generators.sat_generator import (
    generate_3sat_instance, 
    generate_satisfiable_3sat_instance,
    get_default_config,
    SATInstance,
    DEFAULT_CONFIGS
)
from core.data_models import ProblemInstance


class TestSATInstance(unittest.TestCase):
    """Test cases for the SATInstance class."""
    
    def test_sat_instance_creation(self):
        """Test basic SAT instance creation."""
        clauses = [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]
        instance = SATInstance(3, clauses)
        
        self.assertEqual(instance.num_variables, 3)
        self.assertEqual(instance.clauses, clauses)
    
    def test_sat_instance_string_representation(self):
        """Test string representation of SAT instance."""
        clauses = [[1, -2, 3]]
        instance = SATInstance(3, clauses)
        str_repr = str(instance)
        
        self.assertIn("3-SAT instance", str_repr)
        self.assertIn("3 variables", str_repr)
        self.assertIn("1 clauses", str_repr)
        self.assertIn("x1", str_repr)
        self.assertIn("¬x2", str_repr)
        self.assertIn("x3", str_repr)


class TestGenerate3SATInstance(unittest.TestCase):
    """Test cases for the generate_3sat_instance function."""
    
    def test_basic_generation(self):
        """Test basic 3-SAT instance generation."""
        instance = generate_3sat_instance(5, 10, seed=42)
        
        # Check that it returns a ProblemInstance
        self.assertIsInstance(instance, ProblemInstance)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "SAT")
        self.assertEqual(instance.size, 5)
        self.assertEqual(instance.parameters["num_variables"], 5)
        self.assertEqual(instance.parameters["num_clauses"], 10)
        self.assertEqual(instance.parameters["seed"], 42)
        
        # Check the SAT instance data
        sat_data = instance.data
        self.assertIsInstance(sat_data, SATInstance)
        self.assertEqual(sat_data.num_variables, 5)
        self.assertEqual(len(sat_data.clauses), 10)
        
        # Check that each clause has exactly 3 literals
        for clause in sat_data.clauses:
            self.assertEqual(len(clause), 3)
            
            # Check that all literals are within valid range
            for literal in clause:
                self.assertNotEqual(literal, 0)  # No zero literals
                self.assertLessEqual(abs(literal), 5)  # Within variable range
    
    def test_reproducible_generation(self):
        """Test that generation is reproducible with the same seed."""
        instance1 = generate_3sat_instance(4, 8, seed=123)
        instance2 = generate_3sat_instance(4, 8, seed=123)
        
        # Should generate identical instances
        self.assertEqual(instance1.data.clauses, instance2.data.clauses)
    
    def test_different_seeds_produce_different_instances(self):
        """Test that different seeds produce different instances."""
        instance1 = generate_3sat_instance(4, 8, seed=123)
        instance2 = generate_3sat_instance(4, 8, seed=456)
        
        # Should generate different instances (with high probability)
        self.assertNotEqual(instance1.data.clauses, instance2.data.clauses)
    
    def test_clause_literal_validity(self):
        """Test that generated clauses contain valid literals."""
        instance = generate_3sat_instance(6, 15, seed=789)
        sat_data = instance.data
        
        for clause in sat_data.clauses:
            # Each clause should have exactly 3 literals
            self.assertEqual(len(clause), 3)
            
            # All literals should be non-zero and within variable range
            for literal in clause:
                self.assertNotEqual(literal, 0)
                self.assertGreaterEqual(abs(literal), 1)
                self.assertLessEqual(abs(literal), 6)
            
            # All literals in a clause should be distinct variables
            variables_in_clause = [abs(literal) for literal in clause]
            self.assertEqual(len(variables_in_clause), len(set(variables_in_clause)))
    
    def test_metadata_generation(self):
        """Test that metadata is correctly generated."""
        instance = generate_3sat_instance(8, 20, seed=999)
        
        # Check metadata fields
        self.assertIn("clause_to_variable_ratio", instance.metadata)
        self.assertIn("total_literals", instance.metadata)
        self.assertIn("generation_method", instance.metadata)
        
        # Check metadata values
        self.assertEqual(instance.metadata["clause_to_variable_ratio"], 20 / 8)
        self.assertEqual(instance.metadata["total_literals"], 20 * 3)
        self.assertEqual(instance.metadata["generation_method"], "random_3sat")
    
    def test_parameter_validation(self):
        """Test parameter validation for invalid inputs."""
        # Test invalid number of variables
        with self.assertRaises(ValueError):
            generate_3sat_instance(2, 5)  # Less than 3 variables
        
        with self.assertRaises(ValueError):
            generate_3sat_instance(0, 5)  # Zero variables
        
        with self.assertRaises(ValueError):
            generate_3sat_instance(-1, 5)  # Negative variables
        
        # Test invalid number of clauses
        with self.assertRaises(ValueError):
            generate_3sat_instance(5, 0)  # Zero clauses
        
        with self.assertRaises(ValueError):
            generate_3sat_instance(5, -1)  # Negative clauses
    
    def test_minimum_valid_parameters(self):
        """Test generation with minimum valid parameters."""
        instance = generate_3sat_instance(3, 1, seed=111)
        
        self.assertEqual(instance.size, 3)
        self.assertEqual(len(instance.data.clauses), 1)
        self.assertEqual(len(instance.data.clauses[0]), 3)


class TestGenerateSatisfiable3SATInstance(unittest.TestCase):
    """Test cases for the generate_satisfiable_3sat_instance function."""
    
    def test_basic_satisfiable_generation(self):
        """Test basic satisfiable 3-SAT instance generation."""
        instance = generate_satisfiable_3sat_instance(5, 10, seed=42)
        
        # Check that it returns a ProblemInstance
        self.assertIsInstance(instance, ProblemInstance)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "SAT")
        self.assertEqual(instance.size, 5)
        self.assertEqual(instance.parameters["guaranteed_satisfiable"], True)
        
        # Check metadata
        self.assertEqual(instance.metadata["generation_method"], "satisfiable_3sat")
        self.assertIn("satisfying_assignment", instance.metadata)
        
        # Check that satisfying assignment has correct length
        assignment = instance.metadata["satisfying_assignment"]
        self.assertEqual(len(assignment), 5)
        self.assertTrue(all(isinstance(val, bool) for val in assignment))
    
    def test_satisfying_assignment_validity(self):
        """Test that the generated instance is actually satisfied by the stored assignment."""
        instance = generate_satisfiable_3sat_instance(4, 8, seed=123)
        sat_data = instance.data
        assignment = instance.metadata["satisfying_assignment"]
        
        # Check that every clause is satisfied by the assignment
        for clause in sat_data.clauses:
            clause_satisfied = False
            for literal in clause:
                var_index = abs(literal) - 1
                if literal > 0:
                    # Positive literal: satisfied if variable is True
                    if assignment[var_index]:
                        clause_satisfied = True
                        break
                else:
                    # Negative literal: satisfied if variable is False
                    if not assignment[var_index]:
                        clause_satisfied = True
                        break
            
            self.assertTrue(clause_satisfied, f"Clause {clause} not satisfied by assignment {assignment}")
    
    def test_reproducible_satisfiable_generation(self):
        """Test that satisfiable generation is reproducible with the same seed."""
        instance1 = generate_satisfiable_3sat_instance(4, 6, seed=456)
        instance2 = generate_satisfiable_3sat_instance(4, 6, seed=456)
        
        # Should generate identical instances
        self.assertEqual(instance1.data.clauses, instance2.data.clauses)
        self.assertEqual(instance1.metadata["satisfying_assignment"], 
                        instance2.metadata["satisfying_assignment"])
    
    def test_satisfiable_parameter_validation(self):
        """Test parameter validation for satisfiable instance generation."""
        # Test invalid number of variables
        with self.assertRaises(ValueError):
            generate_satisfiable_3sat_instance(2, 5)
        
        # Test invalid number of clauses
        with self.assertRaises(ValueError):
            generate_satisfiable_3sat_instance(5, 0)


class TestDefaultConfigs(unittest.TestCase):
    """Test cases for default configuration functionality."""
    
    def test_get_default_config_valid_sizes(self):
        """Test getting default configurations for valid sizes."""
        for size in ["small", "medium", "large", "extra_large"]:
            config = get_default_config(size)
            
            # Check that config is a dictionary with required keys
            self.assertIsInstance(config, dict)
            self.assertIn("num_variables", config)
            self.assertIn("num_clauses", config)
            
            # Check that values are positive integers
            self.assertIsInstance(config["num_variables"], int)
            self.assertIsInstance(config["num_clauses"], int)
            self.assertGreater(config["num_variables"], 0)
            self.assertGreater(config["num_clauses"], 0)
            
            # Check that variables >= 3 for 3-SAT
            self.assertGreaterEqual(config["num_variables"], 3)
    
    def test_get_default_config_invalid_size(self):
        """Test getting default configuration for invalid size."""
        with self.assertRaises(ValueError):
            get_default_config("invalid_size")
    
    def test_default_configs_structure(self):
        """Test that DEFAULT_CONFIGS has the expected structure."""
        expected_sizes = ["small", "medium", "large", "extra_large"]
        
        # Check that all expected sizes are present
        for size in expected_sizes:
            self.assertIn(size, DEFAULT_CONFIGS)
        
        # Check that configurations are reasonable (increasing sizes)
        small_vars = DEFAULT_CONFIGS["small"]["num_variables"]
        medium_vars = DEFAULT_CONFIGS["medium"]["num_variables"]
        large_vars = DEFAULT_CONFIGS["large"]["num_variables"]
        extra_large_vars = DEFAULT_CONFIGS["extra_large"]["num_variables"]
        
        self.assertLess(small_vars, medium_vars)
        self.assertLess(medium_vars, large_vars)
        self.assertLess(large_vars, extra_large_vars)
    
    def test_config_copy_independence(self):
        """Test that get_default_config returns independent copies."""
        config1 = get_default_config("small")
        config2 = get_default_config("small")
        
        # Modify one config
        config1["num_variables"] = 999
        
        # Other config should be unchanged
        self.assertNotEqual(config1["num_variables"], config2["num_variables"])


if __name__ == "__main__":
    unittest.main()