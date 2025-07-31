"""
Traveling Salesman Problem (TSP) instance generator.

This module provides functionality to generate TSP problem instances
with configurable parameters for educational and benchmarking purposes.
"""

import random
import math
from typing import List, Dict, Any, Tuple
from core.data_models import ProblemInstance


class TSPInstance:
    """
    Represents a Traveling Salesman Problem instance.
    
    A TSP instance consists of a set of cities and distances between them.
    The goal is to find the shortest tour that visits each city exactly once
    and returns to the starting city.
    """
    
    def __init__(self, num_cities: int, distance_matrix: List[List[float]]):
        """
        Initialize a TSP instance.
        
        Args:
            num_cities: Number of cities in the instance
            distance_matrix: Square matrix of distances between cities
        """
        self.num_cities = num_cities
        self.distance_matrix = distance_matrix
    
    def get_distance(self, city1: int, city2: int) -> float:
        """
        Get the distance between two cities.
        
        Args:
            city1: Index of the first city (0-based)
            city2: Index of the second city (0-based)
        
        Returns:
            Distance between the two cities
        """
        return self.distance_matrix[city1][city2]
    
    def calculate_tour_distance(self, tour: List[int]) -> float:
        """
        Calculate the total distance of a tour.
        
        Args:
            tour: List of city indices representing the tour order
        
        Returns:
            Total distance of the tour
        """
        if len(tour) != self.num_cities:
            raise ValueError(f"Tour must visit all {self.num_cities} cities")
        
        total_distance = 0.0
        for i in range(len(tour)):
            current_city = tour[i]
            next_city = tour[(i + 1) % len(tour)]  # Return to start city
            total_distance += self.get_distance(current_city, next_city)
        
        return total_distance
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the TSP instance."""
        result = f"TSP instance with {self.num_cities} cities:\n"
        result += "Distance matrix:\n"
        for i in range(self.num_cities):
            row = "  "
            for j in range(self.num_cities):
                row += f"{self.distance_matrix[i][j]:6.1f} "
            result += row + "\n"
        return result


def generate_random_tsp_instance(num_cities: int, max_distance: float = 100.0, seed: int = None) -> ProblemInstance:
    """
    Generate a random TSP problem instance.
    
    Creates a TSP instance with random distances between cities.
    The distance matrix is symmetric and satisfies the triangle inequality.
    
    Args:
        num_cities: Number of cities (must be >= 2)
        max_distance: Maximum distance between any two cities
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated TSP data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if num_cities < 2:
        raise ValueError("Number of cities must be at least 2")
    if max_distance <= 0:
        raise ValueError("Maximum distance must be positive")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Initialize distance matrix
    distance_matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
    
    # Generate random distances for upper triangle
    for i in range(num_cities):
        for j in range(i + 1, num_cities):
            distance = random.uniform(1.0, max_distance)
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance  # Symmetric matrix
    
    # Create the TSP instance
    tsp_instance = TSPInstance(num_cities, distance_matrix)
    
    # Calculate some statistics
    all_distances = [distance_matrix[i][j] for i in range(num_cities) for j in range(i + 1, num_cities)]
    avg_distance = sum(all_distances) / len(all_distances)
    min_distance = min(all_distances)
    max_distance_actual = max(all_distances)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="TSP",
        size=num_cities,
        parameters={
            "num_cities": num_cities,
            "max_distance": max_distance,
            "seed": seed
        },
        data=tsp_instance,
        metadata={
            "generation_method": "random",
            "average_distance": avg_distance,
            "min_distance": min_distance,
            "max_distance_actual": max_distance_actual,
            "is_symmetric": True,
            "satisfies_triangle_inequality": False  # Random distances may not satisfy this
        }
    )
    
    return problem_instance


def generate_euclidean_tsp_instance(num_cities: int, grid_size: float = 100.0, seed: int = None) -> ProblemInstance:
    """
    Generate a Euclidean TSP problem instance.
    
    Creates a TSP instance where cities are placed randomly in a 2D plane
    and distances are calculated using Euclidean distance. This guarantees
    the triangle inequality is satisfied.
    
    Args:
        num_cities: Number of cities (must be >= 2)
        grid_size: Size of the square grid where cities are placed
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated Euclidean TSP data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if num_cities < 2:
        raise ValueError("Number of cities must be at least 2")
    if grid_size <= 0:
        raise ValueError("Grid size must be positive")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate random city coordinates
    cities = []
    for _ in range(num_cities):
        x = random.uniform(0, grid_size)
        y = random.uniform(0, grid_size)
        cities.append((x, y))
    
    # Calculate Euclidean distances
    distance_matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
    
    for i in range(num_cities):
        for j in range(num_cities):
            if i != j:
                x1, y1 = cities[i]
                x2, y2 = cities[j]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                distance_matrix[i][j] = distance
    
    # Create the TSP instance
    tsp_instance = TSPInstance(num_cities, distance_matrix)
    
    # Calculate some statistics
    all_distances = [distance_matrix[i][j] for i in range(num_cities) for j in range(i + 1, num_cities)]
    avg_distance = sum(all_distances) / len(all_distances)
    min_distance = min(all_distances)
    max_distance_actual = max(all_distances)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="TSP",
        size=num_cities,
        parameters={
            "num_cities": num_cities,
            "grid_size": grid_size,
            "seed": seed
        },
        data=tsp_instance,
        metadata={
            "generation_method": "euclidean",
            "city_coordinates": cities,
            "average_distance": avg_distance,
            "min_distance": min_distance,
            "max_distance_actual": max_distance_actual,
            "is_symmetric": True,
            "satisfies_triangle_inequality": True
        }
    )
    
    return problem_instance


def generate_clustered_tsp_instance(num_cities: int, num_clusters: int = 3, cluster_radius: float = 20.0, 
                                  grid_size: float = 100.0, seed: int = None) -> ProblemInstance:
    """
    Generate a clustered TSP problem instance.
    
    Creates a TSP instance where cities are grouped into clusters.
    This creates a more structured problem that can be useful for
    testing different algorithmic approaches.
    
    Args:
        num_cities: Number of cities (must be >= 2)
        num_clusters: Number of clusters to create (must be >= 1)
        cluster_radius: Maximum distance from cluster center
        grid_size: Size of the square grid where cluster centers are placed
        seed: Random seed for reproducible generation (optional)
    
    Returns:
        ProblemInstance: A problem instance containing the generated clustered TSP data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if num_cities < 2:
        raise ValueError("Number of cities must be at least 2")
    if num_clusters < 1:
        raise ValueError("Number of clusters must be at least 1")
    if cluster_radius <= 0:
        raise ValueError("Cluster radius must be positive")
    if grid_size <= 0:
        raise ValueError("Grid size must be positive")
    
    # Set random seed if provided for reproducible results
    if seed is not None:
        random.seed(seed)
    
    # Generate cluster centers
    cluster_centers = []
    for _ in range(num_clusters):
        x = random.uniform(cluster_radius, grid_size - cluster_radius)
        y = random.uniform(cluster_radius, grid_size - cluster_radius)
        cluster_centers.append((x, y))
    
    # Assign cities to clusters and generate coordinates
    cities = []
    cities_per_cluster = num_cities // num_clusters
    remaining_cities = num_cities % num_clusters
    
    for cluster_idx in range(num_clusters):
        center_x, center_y = cluster_centers[cluster_idx]
        
        # Determine how many cities to place in this cluster
        cluster_size = cities_per_cluster
        if cluster_idx < remaining_cities:
            cluster_size += 1
        
        # Generate cities around the cluster center
        for _ in range(cluster_size):
            # Generate random angle and distance from center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            # Ensure city stays within grid bounds
            x = max(0, min(grid_size, x))
            y = max(0, min(grid_size, y))
            
            cities.append((x, y))
    
    # Calculate Euclidean distances
    distance_matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
    
    for i in range(num_cities):
        for j in range(num_cities):
            if i != j:
                x1, y1 = cities[i]
                x2, y2 = cities[j]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                distance_matrix[i][j] = distance
    
    # Create the TSP instance
    tsp_instance = TSPInstance(num_cities, distance_matrix)
    
    # Calculate some statistics
    all_distances = [distance_matrix[i][j] for i in range(num_cities) for j in range(i + 1, num_cities)]
    avg_distance = sum(all_distances) / len(all_distances)
    min_distance = min(all_distances)
    max_distance_actual = max(all_distances)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="TSP",
        size=num_cities,
        parameters={
            "num_cities": num_cities,
            "num_clusters": num_clusters,
            "cluster_radius": cluster_radius,
            "grid_size": grid_size,
            "seed": seed
        },
        data=tsp_instance,
        metadata={
            "generation_method": "clustered",
            "city_coordinates": cities,
            "cluster_centers": cluster_centers,
            "average_distance": avg_distance,
            "min_distance": min_distance,
            "max_distance_actual": max_distance_actual,
            "is_symmetric": True,
            "satisfies_triangle_inequality": True
        }
    )
    
    return problem_instance


def generate_grid_tsp_instance(grid_width: int, grid_height: int = None, spacing: float = 10.0) -> ProblemInstance:
    """
    Generate a grid-based TSP problem instance.
    
    Creates a TSP instance where cities are arranged in a regular grid pattern.
    This creates a highly structured problem useful for testing and education.
    
    Args:
        grid_width: Width of the grid (number of cities horizontally)
        grid_height: Height of the grid (defaults to grid_width for square grid)
        spacing: Distance between adjacent cities in the grid
    
    Returns:
        ProblemInstance: A problem instance containing the generated grid TSP data
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    if grid_width < 1:
        raise ValueError("Grid width must be at least 1")
    if grid_height is None:
        grid_height = grid_width
    if grid_height < 1:
        raise ValueError("Grid height must be at least 1")
    if spacing <= 0:
        raise ValueError("Spacing must be positive")
    
    num_cities = grid_width * grid_height
    
    if num_cities < 2:
        raise ValueError("Grid must contain at least 2 cities")
    
    # Generate grid coordinates
    cities = []
    for row in range(grid_height):
        for col in range(grid_width):
            x = col * spacing
            y = row * spacing
            cities.append((x, y))
    
    # Calculate Euclidean distances
    distance_matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
    
    for i in range(num_cities):
        for j in range(num_cities):
            if i != j:
                x1, y1 = cities[i]
                x2, y2 = cities[j]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                distance_matrix[i][j] = distance
    
    # Create the TSP instance
    tsp_instance = TSPInstance(num_cities, distance_matrix)
    
    # Calculate some statistics
    all_distances = [distance_matrix[i][j] for i in range(num_cities) for j in range(i + 1, num_cities)]
    avg_distance = sum(all_distances) / len(all_distances)
    min_distance = min(all_distances)
    max_distance_actual = max(all_distances)
    
    # Create problem instance with metadata
    problem_instance = ProblemInstance(
        problem_type="TSP",
        size=num_cities,
        parameters={
            "grid_width": grid_width,
            "grid_height": grid_height,
            "spacing": spacing
        },
        data=tsp_instance,
        metadata={
            "generation_method": "grid",
            "city_coordinates": cities,
            "average_distance": avg_distance,
            "min_distance": min_distance,
            "max_distance_actual": max_distance_actual,
            "is_symmetric": True,
            "satisfies_triangle_inequality": True
        }
    )
    
    return problem_instance


def validate_distance_matrix(distance_matrix: List[List[float]], tolerance: float = 1e-9) -> Dict[str, bool]:
    """
    Validate properties of a distance matrix.
    
    Checks if the distance matrix satisfies key properties expected for TSP instances:
    - Symmetry: distance[i][j] == distance[j][i]
    - Triangle inequality: distance[i][k] <= distance[i][j] + distance[j][k]
    - Zero diagonal: distance[i][i] == 0
    
    Args:
        distance_matrix: Square matrix of distances
        tolerance: Numerical tolerance for floating-point comparisons
    
    Returns:
        Dict with boolean values for each property check
    """
    n = len(distance_matrix)
    
    # Check if matrix is square
    is_square = all(len(row) == n for row in distance_matrix)
    if not is_square:
        return {
            "is_square": False,
            "is_symmetric": False,
            "has_zero_diagonal": False,
            "satisfies_triangle_inequality": False
        }
    
    # Check symmetry
    is_symmetric = True
    for i in range(n):
        for j in range(n):
            if abs(distance_matrix[i][j] - distance_matrix[j][i]) > tolerance:
                is_symmetric = False
                break
        if not is_symmetric:
            break
    
    # Check zero diagonal
    has_zero_diagonal = all(abs(distance_matrix[i][i]) <= tolerance for i in range(n))
    
    # Check triangle inequality
    satisfies_triangle_inequality = True
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if i != j and j != k and i != k:
                    if distance_matrix[i][k] > distance_matrix[i][j] + distance_matrix[j][k] + tolerance:
                        satisfies_triangle_inequality = False
                        break
            if not satisfies_triangle_inequality:
                break
        if not satisfies_triangle_inequality:
            break
    
    return {
        "is_square": is_square,
        "is_symmetric": is_symmetric,
        "has_zero_diagonal": has_zero_diagonal,
        "satisfies_triangle_inequality": satisfies_triangle_inequality
    }


# Default parameter configurations for common use cases
DEFAULT_CONFIGS = {
    "small": {"num_cities": 4, "max_distance": 50.0},
    "medium": {"num_cities": 6, "max_distance": 100.0},
    "large": {"num_cities": 8, "max_distance": 150.0},
    "extra_large": {"num_cities": 10, "max_distance": 200.0}
}


def get_default_config(size: str) -> Dict[str, Any]:
    """
    Get default configuration parameters for common problem sizes.
    
    Args:
        size: Size category ("small", "medium", "large", "extra_large")
    
    Returns:
        Dict containing num_cities and max_distance for the specified size
    
    Raises:
        ValueError: If the size category is not recognized
    """
    if size not in DEFAULT_CONFIGS:
        available_sizes = ", ".join(DEFAULT_CONFIGS.keys())
        raise ValueError(f"Unknown size '{size}'. Available sizes: {available_sizes}")
    
    return DEFAULT_CONFIGS[size].copy()