"""
Unit tests for TSP solver implementations.

This module contains comprehensive tests for the TSP solver algorithms,
including correctness verification, edge case handling, and performance characteristics.
"""

import unittest
from core.traveling_salesman import (
    TSPBruteForce, TSPNearestNeighbor, TSPNearestNeighborWith2Opt,
    TSPResult, verify_tsp_solution, calculate_tour_improvement
)
from generators.tsp_generator import TSPInstance, generate_random_tsp_instance, generate_euclidean_tsp_instance


class TestTSPBruteForce(unittest.TestCase):
    """Test cases for the TSPBruteForce class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = TSPBruteForce()
    
    def test_solver_interface(self):
        """Test that solver implements the required interface."""
        self.assertEqual(self.solver.get_complexity_class(), "NP-Complete (Factorial Time)")
        self.assertEqual(self.solver.get_algorithm_name(), "Brute Force TSP Solver")
    
    def test_two_city_instance(self):
        """Test solver on a 2-city instance."""
        distance_matrix = [
            [0.0, 10.0],
            [10.0, 0.0]
        ]
        tsp_instance = TSPInstance(2, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertEqual(result['best_tour'], [0, 1])
        self.assertEqual(result['best_distance'], 20.0)  # 0->1->0
        self.assertEqual(result['tours_tried'], 1)
    
    def test_three_city_instance(self):
        """Test solver on a 3-city instance."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 3)
        self.assertGreater(result['best_distance'], 0)
        self.assertEqual(result['tours_tried'], 2)  # (3-1)! = 2 permutations
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
        
        # Check that the calculated distance matches
        calculated_distance = tsp_instance.calculate_tour_distance(result['best_tour'])
        self.assertEqual(result['best_distance'], calculated_distance)
    
    def test_four_city_instance(self):
        """Test solver on a 4-city instance."""
        distance_matrix = [
            [0.0, 2.0, 9.0, 10.0],
            [1.0, 0.0, 6.0, 4.0],
            [15.0, 7.0, 0.0, 8.0],
            [6.0, 3.0, 12.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 4)
        self.assertEqual(result['tours_tried'], 6)  # (4-1)! = 6 permutations
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
    
    def test_single_city_instance(self):
        """Test solver on a 1-city instance (edge case)."""
        distance_matrix = [[0.0]]
        tsp_instance = TSPInstance(1, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertFalse(result['tour_found'])
        self.assertIsNone(result['best_tour'])
        self.assertEqual(result['best_distance'], float('inf'))
        self.assertEqual(result['tours_tried'], 0)
    
    def test_empty_instance(self):
        """Test solver on an empty instance (edge case)."""
        distance_matrix = []
        tsp_instance = TSPInstance(0, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertFalse(result['tour_found'])
        self.assertIsNone(result['best_tour'])
        self.assertEqual(result['best_distance'], float('inf'))
        self.assertEqual(result['tours_tried'], 0)
    
    def test_invalid_input_type(self):
        """Test solver with invalid input type."""
        with self.assertRaises(TypeError):
            self.solver.solve("not a TSP instance")
    
    def test_optimal_solution_small_instance(self):
        """Test that brute force finds the optimal solution for a small known instance."""
        # Create a simple instance where the optimal tour is clear
        distance_matrix = [
            [0.0, 1.0, 4.0],
            [1.0, 0.0, 2.0],
            [4.0, 2.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        # Optimal tour should be 0->1->2->0 with distance 1+2+4=7
        # or 0->2->1->0 with distance 4+2+1=7
        self.assertTrue(result['tour_found'])
        self.assertEqual(result['best_distance'], 7.0)


class TestTSPNearestNeighbor(unittest.TestCase):
    """Test cases for the TSPNearestNeighbor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = TSPNearestNeighbor()
    
    def test_solver_interface(self):
        """Test that solver implements the required interface."""
        self.assertEqual(self.solver.get_complexity_class(), "Polynomial Time Approximation (O(n^2))")
        self.assertEqual(self.solver.get_algorithm_name(), "Nearest Neighbor TSP Heuristic")
    
    def test_two_city_instance(self):
        """Test solver on a 2-city instance."""
        distance_matrix = [
            [0.0, 10.0],
            [10.0, 0.0]
        ]
        tsp_instance = TSPInstance(2, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertEqual(result['best_tour'], [0, 1])
        self.assertEqual(result['best_distance'], 20.0)
        self.assertIn('starting_city', result)
        self.assertIn('distance_calculations', result)
    
    def test_three_city_instance(self):
        """Test solver on a 3-city instance."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 3)
        self.assertGreater(result['best_distance'], 0)
        self.assertGreater(result['distance_calculations'], 0)
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
    
    def test_four_city_instance(self):
        """Test solver on a 4-city instance."""
        distance_matrix = [
            [0.0, 2.0, 9.0, 10.0],
            [1.0, 0.0, 6.0, 4.0],
            [15.0, 7.0, 0.0, 8.0],
            [6.0, 3.0, 12.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 4)
        self.assertGreater(result['distance_calculations'], 0)
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
    
    def test_single_city_instance(self):
        """Test solver on a 1-city instance (edge case)."""
        distance_matrix = [[0.0]]
        tsp_instance = TSPInstance(1, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertFalse(result['tour_found'])
        self.assertIsNone(result['best_tour'])
        self.assertEqual(result['best_distance'], float('inf'))
    
    def test_nearest_neighbor_logic(self):
        """Test that nearest neighbor logic works correctly."""
        # Create an instance where nearest neighbor choice is clear
        distance_matrix = [
            [0.0, 1.0, 10.0, 10.0],
            [1.0, 0.0, 2.0, 10.0],
            [10.0, 2.0, 0.0, 3.0],
            [10.0, 10.0, 3.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        # The algorithm should find a reasonable tour following nearest neighbors
        self.assertGreater(result['best_distance'], 0)
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))


class TestTSPNearestNeighborWith2Opt(unittest.TestCase):
    """Test cases for the TSPNearestNeighborWith2Opt class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = TSPNearestNeighborWith2Opt()
    
    def test_solver_interface(self):
        """Test that solver implements the required interface."""
        self.assertEqual(self.solver.get_complexity_class(), "Polynomial Time Approximation with Local Search (O(n^3))")
        self.assertEqual(self.solver.get_algorithm_name(), "Nearest Neighbor + 2-Opt TSP Solver")
    
    def test_two_city_instance(self):
        """Test solver on a 2-city instance."""
        distance_matrix = [
            [0.0, 10.0],
            [10.0, 0.0]
        ]
        tsp_instance = TSPInstance(2, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertEqual(result['best_tour'], [0, 1])
        self.assertEqual(result['best_distance'], 20.0)
        self.assertEqual(result['initial_distance'], 20.0)
        self.assertEqual(result['improvement_iterations'], 0)  # No improvement possible
    
    def test_three_city_instance(self):
        """Test solver on a 3-city instance."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 3)
        self.assertGreater(result['best_distance'], 0)
        self.assertIn('initial_distance', result)
        self.assertIn('improvement_iterations', result)
        self.assertGreaterEqual(result['improvement_iterations'], 0)
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
        
        # 2-opt should not make the solution worse
        self.assertLessEqual(result['best_distance'], result['initial_distance'])
    
    def test_four_city_instance_with_improvement(self):
        """Test solver on a 4-city instance where 2-opt can improve."""
        # Create an instance where 2-opt improvement is likely
        distance_matrix = [
            [0.0, 1.0, 10.0, 10.0],
            [1.0, 0.0, 1.0, 10.0],
            [10.0, 1.0, 0.0, 1.0],
            [10.0, 10.0, 1.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIsNotNone(result['best_tour'])
        self.assertEqual(len(result['best_tour']), 4)
        
        # Verify the solution is valid
        self.assertTrue(verify_tsp_solution(tsp_instance, result['best_tour']))
        
        # 2-opt should not make the solution worse
        self.assertLessEqual(result['best_distance'], result['initial_distance'])
    
    def test_improvement_statistics(self):
        """Test that improvement statistics are correctly reported."""
        distance_matrix = [
            [0.0, 5.0, 1.0, 10.0],
            [5.0, 0.0, 10.0, 1.0],
            [1.0, 10.0, 0.0, 5.0],
            [10.0, 1.0, 5.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        result = self.solver.solve(tsp_instance)
        
        self.assertTrue(result['tour_found'])
        self.assertIn('initial_distance', result)
        self.assertIn('improvement_iterations', result)
        self.assertIn('distance_calculations', result)
        
        # Check that statistics are reasonable
        self.assertGreater(result['initial_distance'], 0)
        self.assertGreaterEqual(result['improvement_iterations'], 0)
        self.assertGreater(result['distance_calculations'], 0)


class TestTSPResult(unittest.TestCase):
    """Test cases for the TSPResult class."""
    
    def test_result_creation(self):
        """Test TSP result creation."""
        result = TSPResult(
            tour_found=True,
            best_tour=[0, 1, 2],
            best_distance=25.5,
            tours_tried=6
        )
        
        self.assertTrue(result.tour_found)
        self.assertEqual(result.best_tour, [0, 1, 2])
        self.assertEqual(result.best_distance, 25.5)
        self.assertEqual(result.tours_tried, 6)
    
    def test_result_string_representation(self):
        """Test string representation of TSP result."""
        result = TSPResult(
            tour_found=True,
            best_tour=[0, 1, 2],
            best_distance=25.5,
            tours_tried=6
        )
        
        str_repr = str(result)
        self.assertIn("TOUR FOUND", str_repr)
        self.assertIn("0 -> 1 -> 2 -> 0", str_repr)
        self.assertIn("25.50", str_repr)
        self.assertIn("6", str_repr)
    
    def test_result_no_solution_string(self):
        """Test string representation when no solution found."""
        result = TSPResult(
            tour_found=False,
            tours_tried=10
        )
        
        str_repr = str(result)
        self.assertIn("NO TOUR FOUND", str_repr)
        self.assertIn("10", str_repr)
    
    def test_result_to_dict(self):
        """Test conversion of result to dictionary."""
        result = TSPResult(
            tour_found=True,
            best_tour=[0, 1, 2],
            best_distance=25.5,
            tours_tried=6,
            additional_info={'test_key': 'test_value'}
        )
        
        result_dict = result.to_dict()
        
        self.assertTrue(result_dict['tour_found'])
        self.assertEqual(result_dict['best_tour'], [0, 1, 2])
        self.assertEqual(result_dict['best_distance'], 25.5)
        self.assertEqual(result_dict['tours_tried'], 6)
        self.assertEqual(result_dict['test_key'], 'test_value')


class TestVerifyTSPSolution(unittest.TestCase):
    """Test cases for the verify_tsp_solution function."""
    
    def test_valid_solution(self):
        """Test verification of a valid solution."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        tour = [0, 1, 2]
        
        self.assertTrue(verify_tsp_solution(tsp_instance, tour))
    
    def test_wrong_tour_length(self):
        """Test verification with wrong tour length."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        tour = [0, 1]  # Missing city 2
        
        with self.assertRaises(ValueError):
            verify_tsp_solution(tsp_instance, tour)
    
    def test_missing_city(self):
        """Test verification with missing city."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        tour = [0, 1, 1]  # City 2 missing, city 1 duplicated
        
        with self.assertRaises(ValueError):
            verify_tsp_solution(tsp_instance, tour)
    
    def test_duplicate_city(self):
        """Test verification with duplicate city."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        tour = [0, 1, 1]  # City 1 appears twice
        
        with self.assertRaises(ValueError):
            verify_tsp_solution(tsp_instance, tour)
    
    def test_invalid_city_index(self):
        """Test verification with invalid city index."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        tour = [0, 1, 3]  # City 3 doesn't exist (only 0, 1, 2)
        
        with self.assertRaises(ValueError):
            verify_tsp_solution(tsp_instance, tour)


class TestCalculateTourImprovement(unittest.TestCase):
    """Test cases for the calculate_tour_improvement function."""
    
    def test_improvement_calculation(self):
        """Test calculation of tour improvement."""
        distance_matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        original_tour = [0, 1, 2]  # Distance: 10 + 20 + 15 = 45
        improved_tour = [0, 2, 1]  # Distance: 15 + 20 + 10 = 45 (same in this case)
        
        improvement = calculate_tour_improvement(tsp_instance, original_tour, improved_tour)
        
        self.assertEqual(improvement['original_distance'], 45.0)
        self.assertEqual(improvement['improved_distance'], 45.0)
        self.assertEqual(improvement['absolute_improvement'], 0.0)
        self.assertEqual(improvement['relative_improvement_percent'], 0.0)
        self.assertFalse(improvement['is_improvement'])
    
    def test_actual_improvement(self):
        """Test calculation with actual improvement."""
        distance_matrix = [
            [0.0, 1.0, 10.0],
            [1.0, 0.0, 1.0],
            [10.0, 1.0, 0.0]
        ]
        tsp_instance = TSPInstance(3, distance_matrix)
        
        original_tour = [0, 2, 1]  # Distance: 10 + 1 + 1 = 12
        improved_tour = [0, 1, 2]  # Distance: 1 + 1 + 10 = 12 (same in this symmetric case)
        
        improvement = calculate_tour_improvement(tsp_instance, original_tour, improved_tour)
        
        self.assertEqual(improvement['original_distance'], 12.0)
        self.assertEqual(improvement['improved_distance'], 12.0)
        self.assertIn('absolute_improvement', improvement)
        self.assertIn('relative_improvement_percent', improvement)
        self.assertIn('is_improvement', improvement)


class TestTSPSolverComparison(unittest.TestCase):
    """Test cases comparing different TSP solvers."""
    
    def test_brute_force_vs_nearest_neighbor(self):
        """Test that brute force finds optimal solution while NN finds reasonable solution."""
        # Small instance where we can verify optimality
        distance_matrix = [
            [0.0, 2.0, 9.0, 10.0],
            [1.0, 0.0, 6.0, 4.0],
            [15.0, 7.0, 0.0, 8.0],
            [6.0, 3.0, 12.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        bf_solver = TSPBruteForce()
        nn_solver = TSPNearestNeighbor()
        
        bf_result = bf_solver.solve(tsp_instance)
        nn_result = nn_solver.solve(tsp_instance)
        
        # Both should find valid tours
        self.assertTrue(bf_result['tour_found'])
        self.assertTrue(nn_result['tour_found'])
        
        # Brute force should find optimal or equal solution
        self.assertLessEqual(bf_result['best_distance'], nn_result['best_distance'])
        
        # Both solutions should be valid
        self.assertTrue(verify_tsp_solution(tsp_instance, bf_result['best_tour']))
        self.assertTrue(verify_tsp_solution(tsp_instance, nn_result['best_tour']))
    
    def test_nearest_neighbor_vs_2opt(self):
        """Test that 2-opt improves or equals nearest neighbor solution."""
        distance_matrix = [
            [0.0, 5.0, 1.0, 10.0],
            [5.0, 0.0, 10.0, 1.0],
            [1.0, 10.0, 0.0, 5.0],
            [10.0, 1.0, 5.0, 0.0]
        ]
        tsp_instance = TSPInstance(4, distance_matrix)
        
        nn_solver = TSPNearestNeighbor()
        nn_2opt_solver = TSPNearestNeighborWith2Opt()
        
        nn_result = nn_solver.solve(tsp_instance)
        nn_2opt_result = nn_2opt_solver.solve(tsp_instance)
        
        # Both should find valid tours
        self.assertTrue(nn_result['tour_found'])
        self.assertTrue(nn_2opt_result['tour_found'])
        
        # 2-opt should improve or equal the nearest neighbor solution
        self.assertLessEqual(nn_2opt_result['best_distance'], nn_result['best_distance'])
        
        # Both solutions should be valid
        self.assertTrue(verify_tsp_solution(tsp_instance, nn_result['best_tour']))
        self.assertTrue(verify_tsp_solution(tsp_instance, nn_2opt_result['best_tour']))


if __name__ == "__main__":
    unittest.main()