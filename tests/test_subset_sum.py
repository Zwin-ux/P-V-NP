"""
Unit tests for the Subset Sum solver implementations.

This module contains comprehensive tests for the subset sum solving functionality,
including correctness verification, edge cases, and performance characteristics.
"""

import unittest
from core.subset_sum import (
    SubsetSumBruteForce,
    SubsetSumDP,
    SubsetSumResult,
    verify_subset_sum_solution,
    find_all_subset_sum_solutions
)
from generators.subset_generator import SubsetSumInstance, generate_solvable_subset_sum_instance


class TestSubsetSumBruteForce(unittest.TestCase):
    """Test cases for the SubsetSumBruteForce solver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = SubsetSumBruteForce()
    
    def test_simple_solvable_case(self):
        """Test a simple case with a known solution."""
        numbers = [1, 2, 3, 4, 5]
        target = 7
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['target'], 7)
        self.assertIsInstance(result['solution_subset'], list)
        self.assertIsInstance(result['solution_indices'], list)
        self.assertGreater(result['subsets_tried'], 0)
        
        # Verify the solution is correct
        self.assertEqual(sum(result['solution_subset']), target)
        
        # Verify indices correspond to correct elements
        for i, idx in enumerate(result['solution_indices']):
            self.assertEqual(result['solution_subset'][i], numbers[idx])
    
    def test_unsolvable_case(self):
        """Test a case with no solution."""
        numbers = [2, 4, 6, 8]
        target = 5  # No subset of even numbers can sum to odd number
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertFalse(result['solution_found'])
        self.assertIsNone(result['solution_subset'])
        self.assertIsNone(result['solution_indices'])
        self.assertEqual(result['target'], 5)
        self.assertEqual(result['subsets_tried'], 2 ** len(numbers))  # Should try all subsets
    
    def test_empty_subset_solution(self):
        """Test case where empty subset is the solution."""
        numbers = [1, 2, 3]
        target = 0
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['solution_subset'], [])
        self.assertEqual(result['solution_indices'], [])
        self.assertEqual(sum(result['solution_subset']), 0)
    
    def test_single_element_solution(self):
        """Test case where single element is the solution."""
        numbers = [5, 10, 15]
        target = 10
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['solution_subset'], [10])
        self.assertEqual(result['solution_indices'], [1])
    
    def test_full_set_solution(self):
        """Test case where the entire set is the solution."""
        numbers = [1, 2, 3]
        target = 6  # Sum of all elements
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(sum(result['solution_subset']), 6)
        self.assertEqual(len(result['solution_subset']), 3)
    
    def test_duplicate_numbers(self):
        """Test case with duplicate numbers in the set."""
        numbers = [2, 2, 3, 3]
        target = 5
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(sum(result['solution_subset']), 5)
        # Should find solution like [2, 3] using elements at different indices
    
    def test_large_numbers(self):
        """Test case with larger numbers."""
        numbers = [100, 200, 300, 400]
        target = 500
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(sum(result['solution_subset']), 500)
    
    def test_invalid_input_type(self):
        """Test error handling for invalid input type."""
        with self.assertRaises(TypeError):
            self.solver.solve("not a SubsetSumInstance")
    
    def test_algorithm_properties(self):
        """Test algorithm property methods."""
        self.assertEqual(self.solver.get_complexity_class(), "NP-Complete (Exponential Time)")
        self.assertEqual(self.solver.get_algorithm_name(), "Brute Force Subset Sum Solver")
    
    def test_subset_counting(self):
        """Test that the solver tries the correct number of subsets."""
        numbers = [1, 2, 3]
        target = 10  # Unsolvable
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        # Should try all 2^3 = 8 subsets
        self.assertEqual(result['subsets_tried'], 8)
        self.assertFalse(result['solution_found'])


class TestSubsetSumResult(unittest.TestCase):
    """Test cases for the SubsetSumResult class."""
    
    def test_result_initialization(self):
        """Test SubsetSumResult initialization."""
        result = SubsetSumResult(
            solution_found=True,
            solution_subset=[1, 3],
            solution_indices=[0, 2],
            subsets_tried=5,
            target=4
        )
        
        self.assertTrue(result.solution_found)
        self.assertEqual(result.solution_subset, [1, 3])
        self.assertEqual(result.solution_indices, [0, 2])
        self.assertEqual(result.subsets_tried, 5)
        self.assertEqual(result.target, 4)
    
    def test_result_str_representation_found(self):
        """Test string representation when solution is found."""
        result = SubsetSumResult(
            solution_found=True,
            solution_subset=[2, 3],
            subsets_tried=10,
            target=5
        )
        
        str_repr = str(result)
        self.assertIn("SOLUTION FOUND", str_repr)
        self.assertIn("{2, 3}", str_repr)
        self.assertIn("= 5", str_repr)
        self.assertIn("tried 10", str_repr)
    
    def test_result_str_representation_not_found(self):
        """Test string representation when no solution is found."""
        result = SubsetSumResult(
            solution_found=False,
            subsets_tried=16,
            target=10
        )
        
        str_repr = str(result)
        self.assertIn("NO SOLUTION", str_repr)
        self.assertIn("tried 16", str_repr)
    
    def test_result_to_dict(self):
        """Test conversion to dictionary."""
        result = SubsetSumResult(
            solution_found=True,
            solution_subset=[1, 4],
            solution_indices=[0, 3],
            subsets_tried=8,
            target=5,
            additional_info={"algorithm": "brute_force"}
        )
        
        result_dict = result.to_dict()
        
        self.assertTrue(result_dict['solution_found'])
        self.assertEqual(result_dict['solution_subset'], [1, 4])
        self.assertEqual(result_dict['solution_indices'], [0, 3])
        self.assertEqual(result_dict['subsets_tried'], 8)
        self.assertEqual(result_dict['target'], 5)
        self.assertEqual(result_dict['algorithm'], "brute_force")


class TestVerifySubsetSumSolution(unittest.TestCase):
    """Test cases for the verify_subset_sum_solution function."""
    
    def test_valid_solution(self):
        """Test verification of a valid solution."""
        numbers = [1, 2, 3, 4]
        target = 6
        instance = SubsetSumInstance(numbers, target)
        solution = [2, 4]
        
        self.assertTrue(verify_subset_sum_solution(instance, solution))
    
    def test_invalid_solution_wrong_sum(self):
        """Test verification of solution with wrong sum."""
        numbers = [1, 2, 3, 4]
        target = 6
        instance = SubsetSumInstance(numbers, target)
        solution = [1, 2]  # Sums to 3, not 6
        
        self.assertFalse(verify_subset_sum_solution(instance, solution))
    
    def test_invalid_solution_element_not_in_set(self):
        """Test verification of solution with element not in original set."""
        numbers = [1, 2, 3, 4]
        target = 6
        instance = SubsetSumInstance(numbers, target)
        solution = [2, 5]  # 5 is not in the original set
        
        with self.assertRaises(ValueError):
            verify_subset_sum_solution(instance, solution)
    
    def test_empty_solution(self):
        """Test verification of empty solution."""
        numbers = [1, 2, 3]
        target = 0
        instance = SubsetSumInstance(numbers, target)
        solution = []
        
        self.assertTrue(verify_subset_sum_solution(instance, solution))


class TestFindAllSubsetSumSolutions(unittest.TestCase):
    """Test cases for the find_all_subset_sum_solutions function."""
    
    def test_multiple_solutions(self):
        """Test finding all solutions when multiple exist."""
        numbers = [1, 2, 3, 4]
        target = 5
        instance = SubsetSumInstance(numbers, target)
        
        all_solutions = find_all_subset_sum_solutions(instance)
        
        # Expected solutions: [1, 4] and [2, 3]
        self.assertEqual(len(all_solutions), 2)
        
        # Verify each solution
        for solution in all_solutions:
            self.assertEqual(sum(solution), 5)
            self.assertTrue(verify_subset_sum_solution(instance, solution))
        
        # Check specific solutions (order may vary)
        solution_sets = [set(sol) for sol in all_solutions]
        self.assertIn({1, 4}, solution_sets)
        self.assertIn({2, 3}, solution_sets)
    
    def test_single_solution(self):
        """Test finding all solutions when only one exists."""
        numbers = [1, 3, 5]
        target = 6
        instance = SubsetSumInstance(numbers, target)
        
        all_solutions = find_all_subset_sum_solutions(instance)
        
        self.assertEqual(len(all_solutions), 1)
        self.assertEqual(set(all_solutions[0]), {1, 5})
    
    def test_no_solutions(self):
        """Test finding all solutions when none exist."""
        numbers = [2, 4, 6]
        target = 5
        instance = SubsetSumInstance(numbers, target)
        
        all_solutions = find_all_subset_sum_solutions(instance)
        
        self.assertEqual(len(all_solutions), 0)
    
    def test_empty_subset_solution(self):
        """Test finding empty subset as solution."""
        numbers = [1, 2, 3]
        target = 0
        instance = SubsetSumInstance(numbers, target)
        
        all_solutions = find_all_subset_sum_solutions(instance)
        
        self.assertEqual(len(all_solutions), 1)
        self.assertEqual(all_solutions[0], [])


class TestSubsetSumDP(unittest.TestCase):
    """Test cases for the SubsetSumDP solver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = SubsetSumDP()
    
    def test_simple_solvable_case(self):
        """Test a simple case with a known solution."""
        numbers = [1, 2, 3, 4, 5]
        target = 7
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['target'], 7)
        self.assertIsInstance(result['solution_subset'], list)
        self.assertIsInstance(result['solution_indices'], list)
        self.assertGreater(result['dp_table_size'], 0)
        
        # Verify the solution is correct
        self.assertEqual(sum(result['solution_subset']), target)
        
        # Verify indices correspond to correct elements
        for i, idx in enumerate(result['solution_indices']):
            self.assertEqual(result['solution_subset'][i], numbers[idx])
    
    def test_unsolvable_case(self):
        """Test a case with no solution."""
        numbers = [2, 4, 6, 8]
        target = 5  # No subset of even numbers can sum to odd number
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertFalse(result['solution_found'])
        self.assertIsNone(result['solution_subset'])
        self.assertIsNone(result['solution_indices'])
        self.assertEqual(result['target'], 5)
        self.assertGreater(result['dp_table_size'], 0)
    
    def test_empty_subset_solution(self):
        """Test case where empty subset is the solution."""
        numbers = [1, 2, 3]
        target = 0
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['solution_subset'], [])
        self.assertEqual(result['solution_indices'], [])
        self.assertEqual(sum(result['solution_subset']), 0)
        self.assertEqual(result['dp_table_size'], 0)  # Special case handling
    
    def test_single_element_solution(self):
        """Test case where single element is the solution."""
        numbers = [5, 10, 15]
        target = 10
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(result['solution_subset'], [10])
        self.assertEqual(result['solution_indices'], [1])
    
    def test_negative_target(self):
        """Test case with negative target."""
        numbers = [1, 2, 3]
        target = -5
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertFalse(result['solution_found'])
        self.assertEqual(result['dp_table_size'], 0)
    
    def test_large_target(self):
        """Test case with target larger than sum of all elements."""
        numbers = [1, 2, 3]
        target = 10  # Sum of all elements is 6
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        self.assertFalse(result['solution_found'])
    
    def test_algorithm_properties(self):
        """Test algorithm property methods."""
        self.assertEqual(self.solver.get_complexity_class(), "Pseudo-polynomial Time (O(n * sum))")
        self.assertEqual(self.solver.get_algorithm_name(), "Dynamic Programming Subset Sum Solver")
    
    def test_dp_table_size_calculation(self):
        """Test that DP table size is calculated correctly."""
        numbers = [1, 2, 3]
        target = 4
        instance = SubsetSumInstance(numbers, target)
        
        result = self.solver.solve(instance)
        
        # Table size should be (n+1) * (target+1) = 4 * 5 = 20
        expected_size = (len(numbers) + 1) * (target + 1)
        self.assertEqual(result['dp_table_size'], expected_size)
    
    def test_invalid_input_type(self):
        """Test error handling for invalid input type."""
        with self.assertRaises(TypeError):
            self.solver.solve("not a SubsetSumInstance")


class TestSolverComparison(unittest.TestCase):
    """Test cases comparing brute force and DP solvers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.brute_force_solver = SubsetSumBruteForce()
        self.dp_solver = SubsetSumDP()
    
    def test_same_results_solvable(self):
        """Test that both solvers give the same result for solvable cases."""
        test_cases = [
            ([1, 2, 3, 4], 5),
            ([2, 4, 6, 8], 10),
            ([1, 3, 5, 7, 9], 12),
            ([10, 20, 30], 50)
        ]
        
        for numbers, target in test_cases:
            with self.subTest(numbers=numbers, target=target):
                instance = SubsetSumInstance(numbers, target)
                
                bf_result = self.brute_force_solver.solve(instance)
                dp_result = self.dp_solver.solve(instance)
                
                # Both should agree on whether solution exists
                self.assertEqual(bf_result['solution_found'], dp_result['solution_found'])
                
                if bf_result['solution_found']:
                    # Both solutions should sum to target
                    self.assertEqual(sum(bf_result['solution_subset']), target)
                    self.assertEqual(sum(dp_result['solution_subset']), target)
    
    def test_same_results_unsolvable(self):
        """Test that both solvers give the same result for unsolvable cases."""
        test_cases = [
            ([2, 4, 6], 5),  # Even numbers, odd target
            ([1, 3, 5], 2),  # No way to make 2
            ([10, 20], 15)   # Gap in possible sums
        ]
        
        for numbers, target in test_cases:
            with self.subTest(numbers=numbers, target=target):
                instance = SubsetSumInstance(numbers, target)
                
                bf_result = self.brute_force_solver.solve(instance)
                dp_result = self.dp_solver.solve(instance)
                
                # Both should agree that no solution exists
                self.assertFalse(bf_result['solution_found'])
                self.assertFalse(dp_result['solution_found'])
    
    def test_performance_characteristics(self):
        """Test that DP solver has different performance characteristics."""
        numbers = [1, 2, 3, 4, 5]
        target = 8
        instance = SubsetSumInstance(numbers, target)
        
        bf_result = self.brute_force_solver.solve(instance)
        dp_result = self.dp_solver.solve(instance)
        
        # Brute force stops when it finds a solution, so it tries <= 2^n subsets
        self.assertLessEqual(bf_result['subsets_tried'], 2 ** len(numbers))
        self.assertGreater(bf_result['subsets_tried'], 0)
        
        # DP uses a table of size (n+1) * (target+1)
        expected_dp_size = (len(numbers) + 1) * (target + 1)
        self.assertEqual(dp_result['dp_table_size'], expected_dp_size)


class TestIntegrationWithGenerator(unittest.TestCase):
    """Integration tests using the subset sum generator."""
    
    def test_solve_generated_solvable_instance_brute_force(self):
        """Test solving a generated solvable instance with brute force."""
        problem = generate_solvable_subset_sum_instance(5, max_value=20, seed=42)
        solver = SubsetSumBruteForce()
        
        result = solver.solve(problem.data)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(sum(result['solution_subset']), problem.data.target)
        
        # Verify against the known solution in metadata
        expected_solution = problem.metadata['solution_subset']
        self.assertEqual(sum(expected_solution), problem.data.target)
    
    def test_solve_generated_solvable_instance_dp(self):
        """Test solving a generated solvable instance with DP."""
        problem = generate_solvable_subset_sum_instance(5, max_value=20, seed=42)
        solver = SubsetSumDP()
        
        result = solver.solve(problem.data)
        
        self.assertTrue(result['solution_found'])
        self.assertEqual(sum(result['solution_subset']), problem.data.target)
        
        # Verify against the known solution in metadata
        expected_solution = problem.metadata['solution_subset']
        self.assertEqual(sum(expected_solution), problem.data.target)
    
    def test_multiple_generated_instances_both_solvers(self):
        """Test solving multiple generated instances with both solvers."""
        bf_solver = SubsetSumBruteForce()
        dp_solver = SubsetSumDP()
        
        for i in range(5):
            with self.subTest(instance=i):
                problem = generate_solvable_subset_sum_instance(4, max_value=10, seed=i)
                
                bf_result = bf_solver.solve(problem.data)
                dp_result = dp_solver.solve(problem.data)
                
                # Both should find solutions
                self.assertTrue(bf_result['solution_found'])
                self.assertTrue(dp_result['solution_found'])
                
                # Both solutions should be correct
                self.assertEqual(sum(bf_result['solution_subset']), problem.data.target)
                self.assertEqual(sum(dp_result['solution_subset']), problem.data.target)


if __name__ == "__main__":
    unittest.main()