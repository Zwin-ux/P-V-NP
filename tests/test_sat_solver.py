"""
Unit tests for SAT solver implementations.

This module contains comprehensive tests for the SAT solver algorithms,
including correctness verification, edge case handling, and performance characteristics.
"""

import unittest
from core.sat_solver import SATBruteForceSolver, SATOptimizedSolver, SATResult, verify_sat_solution
from generators.sat_generator import SATInstance, generate_3sat_instance, generate_satisfiable_3sat_instance


class TestSATBruteForceSolver(unittest.TestCase):
    """Test cases for the SATBruteForceSolver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = SATBruteForceSolver()
    
    def test_solver_interface(self):
        """Test that solver implements the required interface."""
        self.assertEqual(self.solver.get_complexity_class(), "NP-Complete (Exponential Time)")
        self.assertEqual(self.solver.get_algorithm_name(), "Brute Force SAT Solver")
    
    def test_simple_satisfiable_instance(self):
        """Test solver on a simple satisfiable instance."""
        # Create a simple satisfiable instance: (x1 ∨ x2 ∨ x3)
        clauses = [[1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        self.assertEqual(len(result['assignment']), 3)
        self.assertGreater(result['assignments_tried'], 0)
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_simple_unsatisfiable_instance(self):
        """Test solver on a simple unsatisfiable instance."""
        # Create an unsatisfiable instance: (x1) ∧ (¬x1)
        clauses = [[1, 1, 1], [-1, -1, -1]]  # Padding to make it 3-SAT
        sat_instance = SATInstance(1, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertFalse(result['satisfiable'])
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['assignments_tried'], 2)  # Should try both assignments for x1
    
    def test_known_satisfiable_instance(self):
        """Test solver on a known satisfiable instance."""
        # Create instance: (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ ¬x3) ∧ (x1 ∨ x2 ∨ x3)
        # This should be satisfiable with assignment [True, True, True]
        clauses = [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_known_unsatisfiable_instance(self):
        """Test solver on a known unsatisfiable instance."""
        # Create unsatisfiable instance: (x1 ∨ x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ x3) ∧ 
        # (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ ¬x2 ∨ x3) ∧ (x1 ∨ x2 ∨ ¬x3) ∧ 
        # (¬x1 ∨ x2 ∨ ¬x3) ∧ (x1 ∨ ¬x2 ∨ ¬x3) ∧ (¬x1 ∨ ¬x2 ∨ ¬x3)
        clauses = [
            [1, 2, 3], [-1, 2, 3], [1, -2, 3], [-1, -2, 3],
            [1, 2, -3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]
        ]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertFalse(result['satisfiable'])
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['assignments_tried'], 8)  # Should try all 2^3 assignments
    
    def test_single_variable_satisfiable(self):
        """Test solver on single variable satisfiable instance."""
        # Create instance: (x1 ∨ x1 ∨ x1) - satisfiable with x1 = True
        clauses = [[1, 1, 1]]
        sat_instance = SATInstance(1, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertEqual(result['assignment'], [True])
        self.assertLessEqual(result['assignments_tried'], 2)
    
    def test_single_variable_unsatisfiable(self):
        """Test solver on single variable unsatisfiable instance."""
        # Create instance: (¬x1 ∨ ¬x1 ∨ ¬x1) ∧ (x1 ∨ x1 ∨ x1) - unsatisfiable
        clauses = [[-1, -1, -1], [1, 1, 1]]
        sat_instance = SATInstance(1, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertFalse(result['satisfiable'])
        self.assertIsNone(result['assignment'])
        self.assertEqual(result['assignments_tried'], 2)
    
    def test_generated_satisfiable_instance(self):
        """Test solver on generated satisfiable instance."""
        # Generate a guaranteed satisfiable instance
        problem_instance = generate_satisfiable_3sat_instance(4, 6, seed=42)
        sat_instance = problem_instance.data
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        self.assertEqual(len(result['assignment']), 4)
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_assignment_enumeration_order(self):
        """Test that assignments are tried in the expected order."""
        # Create instance that's only satisfied by [False, False, True] (assignment 4 in binary)
        # (¬x1 ∨ ¬x2 ∨ x3)
        clauses = [[-1, -2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        # Should find solution relatively quickly since [False, False, True] is assignment #4
        self.assertLessEqual(result['assignments_tried'], 5)
    
    def test_invalid_input_type(self):
        """Test solver behavior with invalid input type."""
        with self.assertRaises(TypeError):
            self.solver.solve("not a SAT instance")
        
        with self.assertRaises(TypeError):
            self.solver.solve(None)
    
    def test_empty_clauses(self):
        """Test solver on instance with no clauses (trivially satisfiable)."""
        sat_instance = SATInstance(3, [])
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        self.assertEqual(result['assignments_tried'], 1)  # First assignment should work
    
    def test_evaluate_assignment_method(self):
        """Test the internal _evaluate_assignment method."""
        clauses = [[1, -2, 3], [-1, 2, -3]]
        
        # Test assignment that satisfies all clauses
        # [True, True, False] should satisfy:
        # Clause 1: (x1 ∨ ¬x2 ∨ x3) = (True ∨ False ∨ False) = True
        # Clause 2: (¬x1 ∨ x2 ∨ ¬x3) = (False ∨ True ∨ True) = True
        self.assertTrue(self.solver._evaluate_assignment([True, True, False], clauses))
        
        # Test assignment that doesn't satisfy all clauses
        # Create a clearly unsatisfiable case
        unsatisfiable_clauses = [[1, 1, 1], [-1, -1, -1]]  # x1 and ¬x1 - impossible
        self.assertFalse(self.solver._evaluate_assignment([True], unsatisfiable_clauses))
        self.assertFalse(self.solver._evaluate_assignment([False], unsatisfiable_clauses))


class TestSATResult(unittest.TestCase):
    """Test cases for the SATResult class."""
    
    def test_satisfiable_result_creation(self):
        """Test creation of satisfiable result."""
        assignment = [True, False, True]
        result = SATResult(True, assignment, 5)
        
        self.assertTrue(result.satisfiable)
        self.assertEqual(result.assignment, assignment)
        self.assertEqual(result.assignments_tried, 5)
        self.assertEqual(result.additional_info, {})
    
    def test_unsatisfiable_result_creation(self):
        """Test creation of unsatisfiable result."""
        result = SATResult(False, None, 8)
        
        self.assertFalse(result.satisfiable)
        self.assertIsNone(result.assignment)
        self.assertEqual(result.assignments_tried, 8)
    
    def test_result_with_additional_info(self):
        """Test result creation with additional information."""
        additional_info = {"solver_type": "brute_force", "timeout": False}
        result = SATResult(True, [True, True], 3, additional_info)
        
        self.assertEqual(result.additional_info, additional_info)
    
    def test_satisfiable_string_representation(self):
        """Test string representation of satisfiable result."""
        result = SATResult(True, [True, False, True], 7)
        str_repr = str(result)
        
        self.assertIn("SATISFIABLE", str_repr)
        self.assertIn("x1=True", str_repr)
        self.assertIn("x2=False", str_repr)
        self.assertIn("x3=True", str_repr)
        self.assertIn("tried 7 assignments", str_repr)
    
    def test_unsatisfiable_string_representation(self):
        """Test string representation of unsatisfiable result."""
        result = SATResult(False, None, 16)
        str_repr = str(result)
        
        self.assertIn("UNSATISFIABLE", str_repr)
        self.assertIn("tried 16 assignments", str_repr)
    
    def test_to_dict_method(self):
        """Test conversion to dictionary."""
        additional_info = {"method": "exhaustive"}
        result = SATResult(True, [False, True], 4, additional_info)
        
        result_dict = result.to_dict()
        
        expected = {
            'satisfiable': True,
            'assignment': [False, True],
            'assignments_tried': 4,
            'method': 'exhaustive'
        }
        self.assertEqual(result_dict, expected)


class TestVerifySATSolution(unittest.TestCase):
    """Test cases for the verify_sat_solution utility function."""
    
    def test_verify_correct_solution(self):
        """Test verification of a correct solution."""
        clauses = [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        assignment = [True, True, True]
        
        self.assertTrue(verify_sat_solution(sat_instance, assignment))
    
    def test_verify_incorrect_solution(self):
        """Test verification of an incorrect solution."""
        # Use an assignment that definitely doesn't work
        clauses = [[1, 2, 3], [-1, -2, -3]]  # (x1∨x2∨x3) ∧ (¬x1∨¬x2∨¬x3) - contradictory
        sat_instance = SATInstance(3, clauses)
        assignment = [True, True, True]  # Satisfies first clause but not second
        
        self.assertFalse(verify_sat_solution(sat_instance, assignment))
    
    def test_verify_wrong_assignment_length(self):
        """Test verification with wrong assignment length."""
        clauses = [[1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        assignment = [True, False]  # Too short
        
        with self.assertRaises(ValueError):
            verify_sat_solution(sat_instance, assignment)
        
        assignment = [True, False, True, False]  # Too long
        
        with self.assertRaises(ValueError):
            verify_sat_solution(sat_instance, assignment)
    
    def test_verify_empty_clauses(self):
        """Test verification with no clauses (trivially satisfiable)."""
        sat_instance = SATInstance(2, [])
        assignment = [True, False]
        
        self.assertTrue(verify_sat_solution(sat_instance, assignment))
    
    def test_verify_single_clause(self):
        """Test verification with single clause."""
        clauses = [[1, -2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        # Test satisfying assignment
        self.assertTrue(verify_sat_solution(sat_instance, [True, False, False]))
        self.assertTrue(verify_sat_solution(sat_instance, [False, False, True]))
        
        # Test non-satisfying assignment
        self.assertFalse(verify_sat_solution(sat_instance, [False, True, False]))


class TestSATSolverIntegration(unittest.TestCase):
    """Integration tests combining solver with generator."""
    
    def test_solver_on_generated_instances(self):
        """Test solver on various generated instances."""
        solver = SATBruteForceSolver()
        
        # Test small instances
        for num_vars in [3, 4, 5]:
            for num_clauses in [3, 5, 8]:
                with self.subTest(vars=num_vars, clauses=num_clauses):
                    problem_instance = generate_3sat_instance(num_vars, num_clauses, seed=42)
                    sat_instance = problem_instance.data
                    
                    result = solver.solve(sat_instance)
                    
                    # Check result structure
                    self.assertIn('satisfiable', result)
                    self.assertIn('assignment', result)
                    self.assertIn('assignments_tried', result)
                    
                    # If satisfiable, verify the solution
                    if result['satisfiable']:
                        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_solver_on_guaranteed_satisfiable_instances(self):
        """Test solver on guaranteed satisfiable instances."""
        solver = SATBruteForceSolver()
        
        for num_vars in [3, 4, 5]:
            for num_clauses in [3, 6, 10]:
                with self.subTest(vars=num_vars, clauses=num_clauses):
                    problem_instance = generate_satisfiable_3sat_instance(num_vars, num_clauses, seed=123)
                    sat_instance = problem_instance.data
                    
                    result = solver.solve(sat_instance)
                    
                    # Should always be satisfiable
                    self.assertTrue(result['satisfiable'])
                    self.assertIsNotNone(result['assignment'])
                    
                    # Verify the solution
                    self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))


class TestSATOptimizedSolver(unittest.TestCase):
    """Test cases for the SATOptimizedSolver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = SATOptimizedSolver()
    
    def test_solver_interface(self):
        """Test that solver implements the required interface."""
        self.assertEqual(self.solver.get_complexity_class(), "NP-Complete (Exponential Time - Optimized)")
        self.assertEqual(self.solver.get_algorithm_name(), "DPLL SAT Solver")
    
    def test_simple_satisfiable_instance(self):
        """Test solver on a simple satisfiable instance."""
        # Create a simple satisfiable instance: (x1 ∨ x2 ∨ x3)
        clauses = [[1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        self.assertEqual(len(result['assignment']), 3)
        self.assertIn('unit_propagations', result)
        self.assertIn('pure_eliminations', result)
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_unit_propagation(self):
        """Test that unit propagation works correctly."""
        # Create instance with unit clauses: (x1) ∧ (¬x1 ∨ x2) ∧ (¬x2 ∨ x3)
        clauses = [[1], [-1, 2], [-2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertEqual(result['assignment'], [True, True, True])
        self.assertGreater(result['unit_propagations'], 0)
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_pure_literal_elimination(self):
        """Test that pure literal elimination works correctly."""
        # Create instance where x3 appears only positively: (x1 ∨ x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ x3)
        clauses = [[1, 2, 3], [-1, 2, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        # The solution should be valid regardless of the specific assignment
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
        
        # Test a clearer case where x1 appears only negatively
        clauses = [[-1, 2], [-1, 3]]
        sat_instance = SATInstance(3, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        # x1 should be set to False due to pure literal elimination
        self.assertFalse(result['assignment'][0])  # x1 is index 0
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_known_unsatisfiable_instance(self):
        """Test solver on a known unsatisfiable instance."""
        # Create unsatisfiable instance: (x1) ∧ (¬x1)
        clauses = [[1], [-1]]
        sat_instance = SATInstance(1, clauses)
        
        result = self.solver.solve(sat_instance)
        
        self.assertFalse(result['satisfiable'])
        self.assertIsNone(result['assignment'])
    
    def test_comparison_with_brute_force(self):
        """Test that optimized solver gives same results as brute force."""
        brute_force = SATBruteForceSolver()
        
        # Test on several instances
        test_cases = [
            [[1, 2, 3], [-1, 2, 3], [1, -2, 3]],  # Satisfiable
            [[1, 2], [-1, 2], [1, -2], [-1, -2]],  # Unsatisfiable
            [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]   # Satisfiable
        ]
        
        for i, clauses in enumerate(test_cases):
            with self.subTest(case=i):
                num_vars = max(abs(lit) for clause in clauses for lit in clause)
                sat_instance = SATInstance(num_vars, clauses)
                
                bf_result = brute_force.solve(sat_instance)
                opt_result = self.solver.solve(sat_instance)
                
                # Both should agree on satisfiability
                self.assertEqual(bf_result['satisfiable'], opt_result['satisfiable'])
                
                # If satisfiable, both solutions should be valid
                if bf_result['satisfiable']:
                    self.assertTrue(verify_sat_solution(sat_instance, bf_result['assignment']))
                    self.assertTrue(verify_sat_solution(sat_instance, opt_result['assignment']))
    
    def test_generated_satisfiable_instance(self):
        """Test solver on generated satisfiable instance."""
        # Generate a guaranteed satisfiable instance
        problem_instance = generate_satisfiable_3sat_instance(4, 6, seed=42)
        sat_instance = problem_instance.data
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
        self.assertEqual(len(result['assignment']), 4)
        
        # Verify the solution
        self.assertTrue(verify_sat_solution(sat_instance, result['assignment']))
    
    def test_empty_clauses(self):
        """Test solver on instance with no clauses (trivially satisfiable)."""
        sat_instance = SATInstance(3, [])
        
        result = self.solver.solve(sat_instance)
        
        self.assertTrue(result['satisfiable'])
        self.assertIsNotNone(result['assignment'])
    
    def test_invalid_input_type(self):
        """Test solver behavior with invalid input type."""
        with self.assertRaises(TypeError):
            self.solver.solve("not a SAT instance")
        
        with self.assertRaises(TypeError):
            self.solver.solve(None)
    
    def test_simplify_clauses_method(self):
        """Test the internal _simplify_clauses method."""
        clauses = [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]
        assignment = [True, None, None]  # x1 = True, x2 and x3 unassigned
        
        simplified = self.solver._simplify_clauses(clauses, assignment)
        
        # First clause should be satisfied and removed
        # Second clause should become [2, -3] (since -1 is false)
        # Third clause should be satisfied and removed
        expected = [[2, -3]]
        self.assertEqual(simplified, expected)
    
    def test_find_unit_literal_method(self):
        """Test the internal _find_unit_literal method."""
        clauses = [[1, 2], [3], [-1, -2]]
        
        unit_literal = self.solver._find_unit_literal(clauses)
        self.assertEqual(unit_literal, 3)
        
        # Test with no unit literals
        clauses = [[1, 2], [-1, -2]]
        unit_literal = self.solver._find_unit_literal(clauses)
        self.assertIsNone(unit_literal)
    
    def test_find_pure_literal_method(self):
        """Test the internal _find_pure_literal method."""
        # x3 appears only positively
        clauses = [[1, -2, 3], [-1, 2, 3]]
        
        pure_literal = self.solver._find_pure_literal(clauses)
        self.assertEqual(pure_literal, 3)
        
        # Test with no pure literals
        clauses = [[1, -2, 3], [-1, 2, -3]]
        pure_literal = self.solver._find_pure_literal(clauses)
        self.assertIsNone(pure_literal)
    
    def test_choose_branch_variable_method(self):
        """Test the internal _choose_branch_variable method."""
        assignment = [True, None, False, None]
        
        branch_var = self.solver._choose_branch_variable(assignment)
        self.assertEqual(branch_var, 2)  # First unassigned variable (x2)
        
        # Test with all variables assigned
        assignment = [True, False, True]
        branch_var = self.solver._choose_branch_variable(assignment)
        self.assertIsNone(branch_var)


class TestSATSolverComparison(unittest.TestCase):
    """Test cases comparing brute force and optimized solvers."""
    
    def test_solver_agreement_on_random_instances(self):
        """Test that both solvers agree on randomly generated instances."""
        brute_force = SATBruteForceSolver()
        optimized = SATOptimizedSolver()
        
        # Test on small random instances
        for seed in [42, 123, 456]:
            for num_vars in [3, 4]:
                for num_clauses in [3, 5, 7]:
                    with self.subTest(seed=seed, vars=num_vars, clauses=num_clauses):
                        problem_instance = generate_3sat_instance(num_vars, num_clauses, seed=seed)
                        sat_instance = problem_instance.data
                        
                        bf_result = brute_force.solve(sat_instance)
                        opt_result = optimized.solve(sat_instance)
                        
                        # Both should agree on satisfiability
                        self.assertEqual(bf_result['satisfiable'], opt_result['satisfiable'])
                        
                        # If satisfiable, both solutions should be valid
                        if bf_result['satisfiable']:
                            self.assertTrue(verify_sat_solution(sat_instance, bf_result['assignment']))
                            self.assertTrue(verify_sat_solution(sat_instance, opt_result['assignment']))
    
    def test_optimized_solver_efficiency(self):
        """Test that optimized solver uses fewer assignments on structured instances."""
        brute_force = SATBruteForceSolver()
        optimized = SATOptimizedSolver()
        
        # Create an instance that should benefit from unit propagation
        # (x1) ∧ (¬x1 ∨ x2) ∧ (¬x2 ∨ x3) ∧ (¬x3 ∨ x4)
        clauses = [[1], [-1, 2], [-2, 3], [-3, 4]]
        sat_instance = SATInstance(4, clauses)
        
        bf_result = brute_force.solve(sat_instance)
        opt_result = optimized.solve(sat_instance)
        
        # Both should find it satisfiable
        self.assertTrue(bf_result['satisfiable'])
        self.assertTrue(opt_result['satisfiable'])
        
        # Optimized solver should use fewer assignments due to unit propagation
        self.assertLess(opt_result['assignments_tried'], bf_result['assignments_tried'])
        
        # Optimized solver should have performed unit propagations
        self.assertGreater(opt_result['unit_propagations'], 0)


if __name__ == "__main__":
    unittest.main()