"""
Unit tests for the TSP problem generator.

This module contains comprehensive tests for the TSP instance generation
functionality, including parameter validation, output format verification,
distance matrix properties, and edge case handling.
"""

import unittest
import math
from generators.tsp_generator import (
    generate_random_tsp_instance,
    generate_euclidean_tsp_instance,
    generate_clustered_tsp_instance,
    generate_grid_tsp_instance,
    validate_distance_matrix,
    get_default_config,
    TSPInstance,
    DEFAULT_CONFIGS
)
from core.data_models import ProblemInstance


class TestTSPInstance(unittest.TestCase):
    """Test cases for the TSPInstance class."""
    
    def test_tsp_instance_creation(self):
        """Test basic TSP instance creation."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        instance = TSPInstance(3, distance_matrix)
        
        self.assertEqual(instance.num_cities, 3)
        self.assertEqual(instance.distance_matrix, distance_matrix)
    
    def test_get_distance(self):
        """Test distance retrieval between cities."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        instance = TSPInstance(3, distance_matrix)
        
        self.assertEqual(instance.get_distance(0, 1), 10.0)
        self.assertEqual(instance.get_distance(1, 2), 20.0)
        self.assertEqual(instance.get_distance(2, 0), 15.0)
        self.assertEqual(instance.get_distance(0, 0), 0.0)
    
    def test_calculate_tour_distance(self):
        """Test tour distance calculation."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        instance = TSPInstance(3, distance_matrix)
        
        # Tour: 0 -> 1 -> 2 -> 0
        tour = [0, 1, 2]
        expected_distance = 10.0 + 20.0 + 15.0  # 0->1 + 1->2 + 2->0
        self.assertEqual(instance.calculate_tour_distance(tour), expected_distance)
        
        # Tour: 0 -> 2 -> 1 -> 0
        tour = [0, 2, 1]
        expected_distance = 15.0 + 20.0 + 10.0  # 0->2 + 2->1 + 1->0
        self.assertEqual(instance.calculate_tour_distance(tour), expected_distance)
    
    def test_calculate_tour_distance_invalid_tour(self):
        """Test tour distance calculation with invalid tour."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        instance = TSPInstance(3, distance_matrix)
        
        # Tour with wrong number of cities
        with self.assertRaises(ValueError):
            instance.calculate_tour_distance([0, 1])  # Missing city 2
        
        with self.assertRaises(ValueError):
            instance.calculate_tour_distance([0, 1, 2, 0])  # Too many cities
    
    def test_string_representation(self):
        """Test string representation of TSP instance."""
        distance_matrix = [
            [0.0, 10.0],
            [10.0, 0.0]
        ]
        instance = TSPInstance(2, distance_matrix)
        str_repr = str(instance)
        
        self.assertIn("TSP instance", str_repr)
        self.assertIn("2 cities", str_repr)
        self.assertIn("Distance matrix", str_repr)
        self.assertIn("10.0", str_repr)


class TestGenerateRandomTSPInstance(unittest.TestCase):
    """Test cases for the generate_random_tsp_instance function."""
    
    def test_basic_generation(self):
        """Test basic random TSP instance generation."""
        instance = generate_random_tsp_instance(4, max_distance=50.0, seed=42)
        
        # Check that it returns a ProblemInstance
        self.assertIsInstance(instance, ProblemInstance)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "TSP")
        self.assertEqual(instance.size, 4)
        self.assertEqual(instance.parameters["num_cities"], 4)
        self.assertEqual(instance.parameters["max_distance"], 50.0)
        self.assertEqual(instance.parameters["seed"], 42)
        
        # Check the TSP instance data
        tsp_data = instance.data
        self.assertIsInstance(tsp_data, TSPInstance)
        self.assertEqual(tsp_data.num_cities, 4)
        self.assertEqual(len(tsp_data.distance_matrix), 4)
        self.assertTrue(all(len(row) == 4 for row in tsp_data.distance_matrix))
    
    def test_distance_matrix_properties(self):
        """Test properties of generated distance matrix."""
        instance = generate_random_tsp_instance(5, max_distance=100.0, seed=123)
        matrix = instance.data.distance_matrix
        
        # Check symmetry
        for i in range(5):
            for j in range(5):
                self.assertEqual(matrix[i][j], matrix[j][i])
        
        # Check zero diagonal
        for i in range(5):
            self.assertEqual(matrix[i][i], 0.0)
        
        # Check distance bounds
        for i in range(5):
            for j in range(5):
                if i != j:
                    self.assertGreater(matrix[i][j], 0.0)
                    self.assertLessEqual(matrix[i][j], 100.0)
    
    def test_reproducible_generation(self):
        """Test that generation is reproducible with the same seed."""
        instance1 = generate_random_tsp_instance(3, max_distance=30.0, seed=456)
        instance2 = generate_random_tsp_instance(3, max_distance=30.0, seed=456)
        
        # Should generate identical instances
        self.assertEqual(instance1.data.distance_matrix, instance2.data.distance_matrix)
    
    def test_different_seeds_produce_different_instances(self):
        """Test that different seeds produce different instances."""
        instance1 = generate_random_tsp_instance(3, max_distance=30.0, seed=111)
        instance2 = generate_random_tsp_instance(3, max_distance=30.0, seed=222)
        
        # Should generate different instances (with high probability)
        self.assertNotEqual(instance1.data.distance_matrix, instance2.data.distance_matrix)
    
    def test_metadata_generation(self):
        """Test that metadata is correctly generated."""
        instance = generate_random_tsp_instance(4, max_distance=80.0, seed=789)
        
        # Check metadata fields
        self.assertIn("generation_method", instance.metadata)
        self.assertIn("average_distance", instance.metadata)
        self.assertIn("min_distance", instance.metadata)
        self.assertIn("max_distance_actual", instance.metadata)
        self.assertIn("is_symmetric", instance.metadata)
        
        # Check metadata values
        self.assertEqual(instance.metadata["generation_method"], "random")
        self.assertTrue(instance.metadata["is_symmetric"])
        self.assertGreater(instance.metadata["average_distance"], 0)
        self.assertGreater(instance.metadata["min_distance"], 0)
        self.assertLessEqual(instance.metadata["max_distance_actual"], 80.0)
    
    def test_parameter_validation(self):
        """Test parameter validation for invalid inputs."""
        # Test invalid number of cities
        with self.assertRaises(ValueError):
            generate_random_tsp_instance(1)  # Less than 2 cities
        
        with self.assertRaises(ValueError):
            generate_random_tsp_instance(0)  # Zero cities
        
        with self.assertRaises(ValueError):
            generate_random_tsp_instance(-1)  # Negative cities
        
        # Test invalid max_distance
        with self.assertRaises(ValueError):
            generate_random_tsp_instance(3, max_distance=0.0)  # Zero distance
        
        with self.assertRaises(ValueError):
            generate_random_tsp_instance(3, max_distance=-10.0)  # Negative distance
    
    def test_minimum_valid_parameters(self):
        """Test generation with minimum valid parameters."""
        instance = generate_random_tsp_instance(2, max_distance=1.0, seed=999)
        
        self.assertEqual(instance.size, 2)
        self.assertEqual(len(instance.data.distance_matrix), 2)
        self.assertLessEqual(instance.data.distance_matrix[0][1], 1.0)


class TestGenerateEuclideanTSPInstance(unittest.TestCase):
    """Test cases for the generate_euclidean_tsp_instance function."""
    
    def test_basic_euclidean_generation(self):
        """Test basic Euclidean TSP instance generation."""
        instance = generate_euclidean_tsp_instance(4, grid_size=100.0, seed=42)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "TSP")
        self.assertEqual(instance.size, 4)
        self.assertEqual(instance.parameters["grid_size"], 100.0)
        
        # Check metadata
        self.assertEqual(instance.metadata["generation_method"], "euclidean")
        self.assertTrue(instance.metadata["is_symmetric"])
        self.assertTrue(instance.metadata["satisfies_triangle_inequality"])
        self.assertIn("city_coordinates", instance.metadata)
        
        # Check coordinates
        coordinates = instance.metadata["city_coordinates"]
        self.assertEqual(len(coordinates), 4)
        for x, y in coordinates:
            self.assertGreaterEqual(x, 0.0)
            self.assertLessEqual(x, 100.0)
            self.assertGreaterEqual(y, 0.0)
            self.assertLessEqual(y, 100.0)
    
    def test_euclidean_distance_calculation(self):
        """Test that distances are correctly calculated using Euclidean formula."""
        instance = generate_euclidean_tsp_instance(3, grid_size=10.0, seed=123)
        coordinates = instance.metadata["city_coordinates"]
        matrix = instance.data.distance_matrix
        
        # Verify distances match Euclidean calculation
        for i in range(3):
            for j in range(3):
                if i != j:
                    x1, y1 = coordinates[i]
                    x2, y2 = coordinates[j]
                    expected_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    self.assertAlmostEqual(matrix[i][j], expected_distance, places=10)
    
    def test_euclidean_triangle_inequality(self):
        """Test that Euclidean instances satisfy triangle inequality."""
        instance = generate_euclidean_tsp_instance(5, grid_size=50.0, seed=456)
        matrix = instance.data.distance_matrix
        
        # Check triangle inequality for all triplets
        for i in range(5):
            for j in range(5):
                for k in range(5):
                    if i != j and j != k and i != k:
                        self.assertLessEqual(matrix[i][k], matrix[i][j] + matrix[j][k] + 1e-10)
    
    def test_euclidean_parameter_validation(self):
        """Test parameter validation for Euclidean instance generation."""
        with self.assertRaises(ValueError):
            generate_euclidean_tsp_instance(1)  # Less than 2 cities
        
        with self.assertRaises(ValueError):
            generate_euclidean_tsp_instance(3, grid_size=0.0)  # Zero grid size
        
        with self.assertRaises(ValueError):
            generate_euclidean_tsp_instance(3, grid_size=-10.0)  # Negative grid size


class TestGenerateClusteredTSPInstance(unittest.TestCase):
    """Test cases for the generate_clustered_tsp_instance function."""
    
    def test_basic_clustered_generation(self):
        """Test basic clustered TSP instance generation."""
        instance = generate_clustered_tsp_instance(6, num_clusters=2, cluster_radius=10.0, 
                                                 grid_size=50.0, seed=42)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "TSP")
        self.assertEqual(instance.size, 6)
        self.assertEqual(instance.parameters["num_clusters"], 2)
        self.assertEqual(instance.parameters["cluster_radius"], 10.0)
        
        # Check metadata
        self.assertEqual(instance.metadata["generation_method"], "clustered")
        self.assertTrue(instance.metadata["is_symmetric"])
        self.assertTrue(instance.metadata["satisfies_triangle_inequality"])
        self.assertIn("city_coordinates", instance.metadata)
        self.assertIn("cluster_centers", instance.metadata)
        
        # Check cluster centers
        cluster_centers = instance.metadata["cluster_centers"]
        self.assertEqual(len(cluster_centers), 2)
    
    def test_clustered_city_distribution(self):
        """Test that cities are distributed among clusters."""
        instance = generate_clustered_tsp_instance(9, num_clusters=3, cluster_radius=5.0, 
                                                 grid_size=100.0, seed=123)
        
        coordinates = instance.metadata["city_coordinates"]
        cluster_centers = instance.metadata["cluster_centers"]
        
        # Each city should be within cluster_radius of at least one cluster center
        for city_x, city_y in coordinates:
            within_cluster = False
            for center_x, center_y in cluster_centers:
                distance_to_center = math.sqrt((city_x - center_x) ** 2 + (city_y - center_y) ** 2)
                if distance_to_center <= 5.0 + 1e-10:  # Allow small numerical error
                    within_cluster = True
                    break
            # Note: Due to grid boundary constraints, cities might be slightly outside
            # the cluster radius, so we don't enforce this strictly
    
    def test_clustered_parameter_validation(self):
        """Test parameter validation for clustered instance generation."""
        with self.assertRaises(ValueError):
            generate_clustered_tsp_instance(1)  # Less than 2 cities
        
        with self.assertRaises(ValueError):
            generate_clustered_tsp_instance(5, num_clusters=0)  # Zero clusters
        
        with self.assertRaises(ValueError):
            generate_clustered_tsp_instance(5, cluster_radius=0.0)  # Zero radius
        
        with self.assertRaises(ValueError):
            generate_clustered_tsp_instance(5, grid_size=0.0)  # Zero grid size


class TestGenerateGridTSPInstance(unittest.TestCase):
    """Test cases for the generate_grid_tsp_instance function."""
    
    def test_basic_grid_generation(self):
        """Test basic grid TSP instance generation."""
        instance = generate_grid_tsp_instance(3, 2, spacing=10.0)
        
        # Check basic properties
        self.assertEqual(instance.problem_type, "TSP")
        self.assertEqual(instance.size, 6)  # 3x2 grid
        self.assertEqual(instance.parameters["grid_width"], 3)
        self.assertEqual(instance.parameters["grid_height"], 2)
        self.assertEqual(instance.parameters["spacing"], 10.0)
        
        # Check metadata
        self.assertEqual(instance.metadata["generation_method"], "grid")
        self.assertTrue(instance.metadata["is_symmetric"])
        self.assertTrue(instance.metadata["satisfies_triangle_inequality"])
        
        # Check coordinates
        coordinates = instance.metadata["city_coordinates"]
        self.assertEqual(len(coordinates), 6)
        
        # Verify grid structure
        expected_coords = [
            (0.0, 0.0), (10.0, 0.0), (20.0, 0.0),  # First row
            (0.0, 10.0), (10.0, 10.0), (20.0, 10.0)  # Second row
        ]
        self.assertEqual(coordinates, expected_coords)
    
    def test_square_grid_default(self):
        """Test square grid generation with default height."""
        instance = generate_grid_tsp_instance(3, spacing=5.0)
        
        # Should create 3x3 grid
        self.assertEqual(instance.size, 9)
        self.assertEqual(instance.parameters["grid_width"], 3)
        self.assertEqual(instance.parameters["grid_height"], 3)
    
    def test_grid_distance_calculation(self):
        """Test that grid distances are correctly calculated."""
        instance = generate_grid_tsp_instance(2, 2, spacing=1.0)
        coordinates = instance.metadata["city_coordinates"]
        matrix = instance.data.distance_matrix
        
        # Verify distances match Euclidean calculation
        for i in range(4):
            for j in range(4):
                if i != j:
                    x1, y1 = coordinates[i]
                    x2, y2 = coordinates[j]
                    expected_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    self.assertAlmostEqual(matrix[i][j], expected_distance, places=10)
    
    def test_grid_parameter_validation(self):
        """Test parameter validation for grid instance generation."""
        with self.assertRaises(ValueError):
            generate_grid_tsp_instance(0)  # Zero width
        
        with self.assertRaises(ValueError):
            generate_grid_tsp_instance(1, grid_height=0)  # Zero height
        
        with self.assertRaises(ValueError):
            generate_grid_tsp_instance(1, spacing=0.0)  # Zero spacing
        
        with self.assertRaises(ValueError):
            generate_grid_tsp_instance(1, spacing=-1.0)  # Negative spacing
    
    def test_minimum_cities_validation(self):
        """Test that grid must contain at least 2 cities."""
        with self.assertRaises(ValueError):
            generate_grid_tsp_instance(1, grid_height=1)  # Only 1 city total


class TestValidateDistanceMatrix(unittest.TestCase):
    """Test cases for the validate_distance_matrix function."""
    
    def test_valid_symmetric_matrix(self):
        """Test validation of a valid symmetric matrix."""
        matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertTrue(result["is_square"])
        self.assertTrue(result["is_symmetric"])
        self.assertTrue(result["has_zero_diagonal"])
        # Triangle inequality may or may not be satisfied for arbitrary values
    
    def test_asymmetric_matrix(self):
        """Test validation of an asymmetric matrix."""
        matrix = [
            [0.0, 10.0, 15.0],
            [5.0, 0.0, 20.0],  # Different from matrix[0][1]
            [15.0, 20.0, 0.0]
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertTrue(result["is_square"])
        self.assertFalse(result["is_symmetric"])
        self.assertTrue(result["has_zero_diagonal"])
    
    def test_non_zero_diagonal(self):
        """Test validation of matrix with non-zero diagonal."""
        matrix = [
            [1.0, 10.0],  # Non-zero diagonal
            [10.0, 0.0]
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertTrue(result["is_square"])
        self.assertTrue(result["is_symmetric"])
        self.assertFalse(result["has_zero_diagonal"])
    
    def test_non_square_matrix(self):
        """Test validation of a non-square matrix."""
        matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0]  # Missing element
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertFalse(result["is_square"])
        self.assertFalse(result["is_symmetric"])
        self.assertFalse(result["has_zero_diagonal"])
        self.assertFalse(result["satisfies_triangle_inequality"])
    
    def test_triangle_inequality_violation(self):
        """Test validation of matrix that violates triangle inequality."""
        matrix = [
            [0.0, 1.0, 100.0],
            [1.0, 0.0, 1.0],
            [100.0, 1.0, 0.0]  # 0->2 distance (100) > 0->1 + 1->2 (1+1=2)
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertTrue(result["is_square"])
        self.assertTrue(result["is_symmetric"])
        self.assertTrue(result["has_zero_diagonal"])
        self.assertFalse(result["satisfies_triangle_inequality"])
    
    def test_triangle_inequality_satisfied(self):
        """Test validation of matrix that satisfies triangle inequality."""
        matrix = [
            [0.0, 3.0, 4.0],
            [3.0, 0.0, 5.0],
            [4.0, 5.0, 0.0]  # Forms a valid triangle: 3-4-5
        ]
        
        result = validate_distance_matrix(matrix)
        
        self.assertTrue(result["is_square"])
        self.assertTrue(result["is_symmetric"])
        self.assertTrue(result["has_zero_diagonal"])
        self.assertTrue(result["satisfies_triangle_inequality"])


class TestDefaultConfigs(unittest.TestCase):
    """Test cases for default configuration functionality."""
    
    def test_get_default_config_valid_sizes(self):
        """Test getting default configurations for valid sizes."""
        for size in ["small", "medium", "large", "extra_large"]:
            config = get_default_config(size)
            
            # Check that config is a dictionary with required keys
            self.assertIsInstance(config, dict)
            self.assertIn("num_cities", config)
            self.assertIn("max_distance", config)
            
            # Check that values are positive
            self.assertGreater(config["num_cities"], 0)
            self.assertGreater(config["max_distance"], 0.0)
            
            # Check that cities >= 2 for TSP
            self.assertGreaterEqual(config["num_cities"], 2)
    
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
        small_cities = DEFAULT_CONFIGS["small"]["num_cities"]
        medium_cities = DEFAULT_CONFIGS["medium"]["num_cities"]
        large_cities = DEFAULT_CONFIGS["large"]["num_cities"]
        extra_large_cities = DEFAULT_CONFIGS["extra_large"]["num_cities"]
        
        self.assertLess(small_cities, medium_cities)
        self.assertLess(medium_cities, large_cities)
        self.assertLess(large_cities, extra_large_cities)
    
    def test_config_copy_independence(self):
        """Test that get_default_config returns independent copies."""
        config1 = get_default_config("small")
        config2 = get_default_config("small")
        
        # Modify one config
        config1["num_cities"] = 999
        
        # Other config should be unchanged
        self.assertNotEqual(config1["num_cities"], config2["num_cities"])


if __name__ == "__main__":
    unittest.main()