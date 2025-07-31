"""
Traveling Salesman Problem (TSP) solver implementations.

This module provides different algorithms for solving the TSP,
including brute-force and optimized approaches for educational and benchmarking purposes.
"""

import itertools
from typing import List, Optional, Dict, Tuple
from core.base_solver import BaseSolver
from generators.tsp_generator import TSPInstance


class TSPBruteForce(BaseSolver):
    """
    Brute-force TSP solver using exhaustive permutation enumeration.
    
    This solver tries all possible permutations of cities to find the shortest tour.
    The time complexity is O(n!) where n is the number of cities, making it
    impractical for more than about 10-12 cities.
    """
    
    def solve(self, problem_instance: TSPInstance) -> Dict:
        """
        Solve the TSP instance using brute-force approach.
        
        Args:
            problem_instance: A TSPInstance containing cities and distances
        
        Returns:
            Dict containing:
                - 'tour_found': bool indicating if a tour was found
                - 'best_tour': List[int] with the optimal tour (city indices)
                - 'best_distance': float with the distance of the optimal tour
                - 'tours_tried': int number of tours evaluated
        """
        if not isinstance(problem_instance, TSPInstance):
            raise TypeError("Expected TSPInstance, got {}".format(type(problem_instance)))
        
        num_cities = problem_instance.num_cities
        
        # Handle edge cases
        if num_cities < 2:
            return {
                'tour_found': False,
                'best_tour': None,
                'best_distance': float('inf'),
                'tours_tried': 0
            }
        
        if num_cities == 2:
            # Only one possible tour for 2 cities
            tour = [0, 1]
            distance = problem_instance.calculate_tour_distance(tour)
            return {
                'tour_found': True,
                'best_tour': tour,
                'best_distance': distance,
                'tours_tried': 1
            }
        
        # For larger instances, try all permutations
        cities = list(range(num_cities))
        best_tour = None
        best_distance = float('inf')
        tours_tried = 0
        
        # Generate all permutations starting from city 0 (to avoid duplicate rotations)
        # We fix the first city to 0 and permute the rest
        for perm in itertools.permutations(cities[1:]):
            tours_tried += 1
            
            # Create full tour starting from city 0
            tour = [0] + list(perm)
            
            # Calculate tour distance
            distance = problem_instance.calculate_tour_distance(tour)
            
            # Update best tour if this one is better
            if distance < best_distance:
                best_distance = distance
                best_tour = tour[:]
        
        return {
            'tour_found': True,
            'best_tour': best_tour,
            'best_distance': best_distance,
            'tours_tried': tours_tried
        }
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "NP-Complete (Factorial Time)"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Brute Force TSP Solver"


class TSPResult:
    """
    Container for TSP solver results with additional utility methods.
    """
    
    def __init__(self, tour_found: bool, best_tour: Optional[List[int]] = None,
                 best_distance: float = float('inf'), tours_tried: int = 0,
                 additional_info: Dict = None):
        """
        Initialize TSP result.
        
        Args:
            tour_found: Whether a tour was found
            best_tour: The best tour found (list of city indices)
            best_distance: Distance of the best tour
            tours_tried: Number of tours evaluated
            additional_info: Additional solver-specific information
        """
        self.tour_found = tour_found
        self.best_tour = best_tour or []
        self.best_distance = best_distance
        self.tours_tried = tours_tried
        self.additional_info = additional_info or {}
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        if self.tour_found:
            tour_str = " -> ".join(map(str, self.best_tour + [self.best_tour[0]]))
            return f"TOUR FOUND: {tour_str} (distance: {self.best_distance:.2f}, tried {self.tours_tried} tours)"
        else:
            return f"NO TOUR FOUND (tried {self.tours_tried} tours)"
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        result = {
            'tour_found': self.tour_found,
            'best_tour': self.best_tour,
            'best_distance': self.best_distance,
            'tours_tried': self.tours_tried
        }
        result.update(self.additional_info)
        return result


class TSPNearestNeighbor(BaseSolver):
    """
    Nearest Neighbor heuristic TSP solver.
    
    This solver uses a greedy approach: starting from a city, always move to the
    nearest unvisited city. The time complexity is O(n^2) where n is the number
    of cities. This provides a polynomial-time approximation but doesn't guarantee
    the optimal solution.
    """
    
    def solve(self, problem_instance: TSPInstance) -> Dict:
        """
        Solve the TSP instance using nearest neighbor heuristic.
        
        Args:
            problem_instance: A TSPInstance containing cities and distances
        
        Returns:
            Dict containing:
                - 'tour_found': bool indicating if a tour was found
                - 'best_tour': List[int] with the heuristic tour (city indices)
                - 'best_distance': float with the distance of the heuristic tour
                - 'starting_city': int the city where the tour started
                - 'distance_calculations': int number of distance calculations performed
        """
        if not isinstance(problem_instance, TSPInstance):
            raise TypeError("Expected TSPInstance, got {}".format(type(problem_instance)))
        
        num_cities = problem_instance.num_cities
        
        # Handle edge cases
        if num_cities < 2:
            return {
                'tour_found': False,
                'best_tour': None,
                'best_distance': float('inf'),
                'starting_city': None,
                'distance_calculations': 0
            }
        
        if num_cities == 2:
            # Only one possible tour for 2 cities
            tour = [0, 1]
            distance = problem_instance.calculate_tour_distance(tour)
            return {
                'tour_found': True,
                'best_tour': tour,
                'best_distance': distance,
                'starting_city': 0,
                'distance_calculations': 2  # 0->1 and 1->0
            }
        
        # Try starting from different cities and pick the best result
        best_tour = None
        best_distance = float('inf')
        best_starting_city = 0
        total_distance_calculations = 0
        
        for start_city in range(num_cities):
            tour, distance, calculations = self._nearest_neighbor_from_city(
                problem_instance, start_city
            )
            total_distance_calculations += calculations
            
            if distance < best_distance:
                best_distance = distance
                best_tour = tour
                best_starting_city = start_city
        
        return {
            'tour_found': True,
            'best_tour': best_tour,
            'best_distance': best_distance,
            'starting_city': best_starting_city,
            'distance_calculations': total_distance_calculations
        }
    
    def _nearest_neighbor_from_city(self, problem_instance: TSPInstance, 
                                   start_city: int) -> Tuple[List[int], float, int]:
        """
        Run nearest neighbor algorithm starting from a specific city.
        
        Args:
            problem_instance: The TSP instance
            start_city: Starting city index
        
        Returns:
            Tuple of (tour, total_distance, distance_calculations)
        """
        num_cities = problem_instance.num_cities
        unvisited = set(range(num_cities))
        tour = [start_city]
        unvisited.remove(start_city)
        current_city = start_city
        total_distance = 0.0
        distance_calculations = 0
        
        # Build tour by always going to nearest unvisited city
        while unvisited:
            nearest_city = None
            nearest_distance = float('inf')
            
            # Find nearest unvisited city
            for city in unvisited:
                distance = problem_instance.get_distance(current_city, city)
                distance_calculations += 1
                
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_city = city
            
            # Move to nearest city
            tour.append(nearest_city)
            unvisited.remove(nearest_city)
            total_distance += nearest_distance
            current_city = nearest_city
        
        # Add distance back to start city to complete the tour
        return_distance = problem_instance.get_distance(current_city, start_city)
        distance_calculations += 1
        total_distance += return_distance
        
        return tour, total_distance, distance_calculations
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "Polynomial Time Approximation (O(n^2))"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Nearest Neighbor TSP Heuristic"


class TSPNearestNeighborWith2Opt(BaseSolver):
    """
    Nearest Neighbor heuristic with 2-opt improvement for TSP.
    
    This solver first finds a tour using the nearest neighbor heuristic,
    then improves it using 2-opt local search. The 2-opt algorithm repeatedly
    looks for two edges in the tour that can be removed and reconnected in a
    different way to reduce the total tour length.
    """
    
    def solve(self, problem_instance: TSPInstance) -> Dict:
        """
        Solve the TSP instance using nearest neighbor + 2-opt improvement.
        
        Args:
            problem_instance: A TSPInstance containing cities and distances
        
        Returns:
            Dict containing:
                - 'tour_found': bool indicating if a tour was found
                - 'best_tour': List[int] with the improved tour (city indices)
                - 'best_distance': float with the distance of the improved tour
                - 'initial_distance': float distance before 2-opt improvement
                - 'improvement_iterations': int number of 2-opt improvements made
                - 'distance_calculations': int total distance calculations performed
        """
        if not isinstance(problem_instance, TSPInstance):
            raise TypeError("Expected TSPInstance, got {}".format(type(problem_instance)))
        
        num_cities = problem_instance.num_cities
        
        # Handle edge cases
        if num_cities < 2:
            return {
                'tour_found': False,
                'best_tour': None,
                'best_distance': float('inf'),
                'initial_distance': float('inf'),
                'improvement_iterations': 0,
                'distance_calculations': 0
            }
        
        if num_cities == 2:
            # Only one possible tour for 2 cities
            tour = [0, 1]
            distance = problem_instance.calculate_tour_distance(tour)
            return {
                'tour_found': True,
                'best_tour': tour,
                'best_distance': distance,
                'initial_distance': distance,
                'improvement_iterations': 0,
                'distance_calculations': 2
            }
        
        # Step 1: Get initial tour using nearest neighbor
        nn_solver = TSPNearestNeighbor()
        nn_result = nn_solver.solve(problem_instance)
        
        if not nn_result['tour_found']:
            return nn_result
        
        initial_tour = nn_result['best_tour']
        initial_distance = nn_result['best_distance']
        distance_calculations = nn_result['distance_calculations']
        
        # Step 2: Improve tour using 2-opt
        improved_tour, improved_distance, improvement_iterations, additional_calculations = \
            self._two_opt_improvement(problem_instance, initial_tour)
        
        distance_calculations += additional_calculations
        
        return {
            'tour_found': True,
            'best_tour': improved_tour,
            'best_distance': improved_distance,
            'initial_distance': initial_distance,
            'improvement_iterations': improvement_iterations,
            'distance_calculations': distance_calculations
        }
    
    def _two_opt_improvement(self, problem_instance: TSPInstance, 
                           initial_tour: List[int]) -> Tuple[List[int], float, int, int]:
        """
        Improve a tour using 2-opt local search.
        
        Args:
            problem_instance: The TSP instance
            initial_tour: Initial tour to improve
        
        Returns:
            Tuple of (improved_tour, improved_distance, iterations, distance_calculations)
        """
        tour = initial_tour[:]
        best_distance = problem_instance.calculate_tour_distance(tour)
        num_cities = len(tour)
        improvement_iterations = 0
        distance_calculations = 0
        improved = True
        
        while improved:
            improved = False
            
            # Try all possible 2-opt swaps
            for i in range(num_cities):
                for j in range(i + 2, num_cities):
                    # Avoid adjacent edges and wrap-around cases that don't change the tour
                    if j == num_cities - 1 and i == 0:
                        continue
                    
                    # Calculate the change in distance if we perform this 2-opt swap
                    # Current edges: (tour[i], tour[i+1]) and (tour[j], tour[(j+1) % num_cities])
                    # New edges: (tour[i], tour[j]) and (tour[i+1], tour[(j+1) % num_cities])
                    
                    current_edge1_dist = problem_instance.get_distance(tour[i], tour[(i + 1) % num_cities])
                    current_edge2_dist = problem_instance.get_distance(tour[j], tour[(j + 1) % num_cities])
                    new_edge1_dist = problem_instance.get_distance(tour[i], tour[j])
                    new_edge2_dist = problem_instance.get_distance(tour[(i + 1) % num_cities], tour[(j + 1) % num_cities])
                    
                    distance_calculations += 4
                    
                    # Calculate change in total distance
                    distance_change = (new_edge1_dist + new_edge2_dist) - (current_edge1_dist + current_edge2_dist)
                    
                    # If this swap improves the tour, perform it
                    if distance_change < -1e-10:  # Use small epsilon for floating point comparison
                        # Perform 2-opt swap: reverse the segment between i+1 and j
                        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                        tour = new_tour
                        best_distance += distance_change
                        improvement_iterations += 1
                        improved = True
                        break
                
                if improved:
                    break
        
        return tour, best_distance, improvement_iterations, distance_calculations
    
    def get_complexity_class(self) -> str:
        """Return the theoretical computational complexity class."""
        return "Polynomial Time Approximation with Local Search (O(n^3))"
    
    def get_algorithm_name(self) -> str:
        """Return a human-readable name for this algorithm."""
        return "Nearest Neighbor + 2-Opt TSP Solver"


def verify_tsp_solution(tsp_instance: TSPInstance, tour: List[int]) -> bool:
    """
    Verify that a given tour is valid for a TSP instance.
    
    This is a utility function that can be used to verify solutions
    from any TSP solver implementation.
    
    Args:
        tsp_instance: The TSP instance to verify against
        tour: The tour to verify (list of city indices)
    
    Returns:
        bool: True if the tour is valid, False otherwise
    
    Raises:
        ValueError: If tour format is invalid
    """
    num_cities = tsp_instance.num_cities
    
    # Check tour length
    if len(tour) != num_cities:
        raise ValueError(f"Tour length ({len(tour)}) doesn't match number of cities ({num_cities})")
    
    # Check that all cities are included exactly once
    if set(tour) != set(range(num_cities)):
        raise ValueError("Tour must visit each city exactly once")
    
    # Check for duplicate cities
    if len(set(tour)) != len(tour):
        raise ValueError("Tour contains duplicate cities")
    
    # If we get here, the tour is valid
    return True


def calculate_tour_improvement(tsp_instance: TSPInstance, 
                             original_tour: List[int], 
                             improved_tour: List[int]) -> Dict:
    """
    Calculate the improvement between two tours.
    
    Args:
        tsp_instance: The TSP instance
        original_tour: The original tour
        improved_tour: The improved tour
    
    Returns:
        Dict containing improvement statistics
    """
    original_distance = tsp_instance.calculate_tour_distance(original_tour)
    improved_distance = tsp_instance.calculate_tour_distance(improved_tour)
    
    absolute_improvement = original_distance - improved_distance
    relative_improvement = (absolute_improvement / original_distance) * 100 if original_distance > 0 else 0
    
    return {
        'original_distance': original_distance,
        'improved_distance': improved_distance,
        'absolute_improvement': absolute_improvement,
        'relative_improvement_percent': relative_improvement,
        'is_improvement': absolute_improvement > 0
    }