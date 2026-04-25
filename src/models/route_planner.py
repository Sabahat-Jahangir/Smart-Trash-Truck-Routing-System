from typing import List, Dict, Tuple, Optional
import numpy as np
from src.models.city_graph import CityGraph
from tabulate import tabulate

class Route:
    def __init__(self, bin_sequence: List[int], total_distance: float, 
                 total_collection: float, truck_capacity: float):
        self.bin_sequence = bin_sequence
        self.total_distance = total_distance
        self.total_collection = total_collection
        self.truck_capacity = truck_capacity
        
    def is_valid(self) -> bool:
        return self.total_collection <= self.truck_capacity
        
    def __str__(self) -> str:
        return (f"Route: {' -> '.join(map(str, self.bin_sequence))}\n"
                f"Total Distance: {self.total_distance:.2f}\n"
                f"Total Collection: {self.total_collection:.2f}/{self.truck_capacity:.2f}")

class RoutePlanner:
    def __init__(self, city_graph: CityGraph):
        self.city_graph = city_graph
        self.routes: List[Route] = []
        self.truck_capacity = 1000.0  # Default capacity
        
    def has_routes(self) -> bool:
        return len(self.routes) > 0
        
    def plan_routes(self, num_trucks: int = 1):
        """Plan routes for the given number of trucks."""
        self.routes = []  # Reset routes
        
        # Get high priority bins first
        high_priority_bins = self.city_graph.get_high_priority_bins()
        remaining_bins = [bin_id for bin_id in self.city_graph.bins.keys()
                         if bin_id not in high_priority_bins]
                         
        # Get clusters of bins
        clusters = self.city_graph.get_bin_clusters(max_distance=50.0)  # Adjustable parameter
        
        # Add isolated bins to their nearest cluster or create single-bin clusters
        isolated_bins = set(remaining_bins)
        for cluster in clusters:
            isolated_bins -= set(cluster)
            
        for bin_id in isolated_bins:
            nearest = self.city_graph.get_nearest_neighbors(bin_id, k=1)
            if nearest:
                nearest_id, _ = nearest[0]
                # Find cluster containing nearest bin and add current bin
                for cluster in clusters:
                    if nearest_id in cluster:
                        cluster.append(bin_id)
                        break
            else:
                clusters.append([bin_id])
                
        # Distribute clusters among trucks
        truck_assignments = self._distribute_clusters(clusters, num_trucks)
        
        # For each truck, optimize route within its assigned clusters
        for truck_idx, assigned_clusters in enumerate(truck_assignments):
            route_bins = []
            for cluster in assigned_clusters:
                route_bins.extend(cluster)
                
            if high_priority_bins:
                # Add high priority bins to the beginning of the route
                route_bins = [bin_id for bin_id in high_priority_bins 
                            if any(bin_id in cluster for cluster in assigned_clusters)] + route_bins
                
            if route_bins:
                route = self._optimize_route(route_bins)
                if route:
                    self.routes.append(route)
                    
    def _distribute_clusters(self, clusters: List[List[int]], num_trucks: int) -> List[List[List[int]]]:
        """Distribute clusters among trucks trying to balance the load."""
        if not clusters:
            return [[] for _ in range(num_trucks)]
            
        # Calculate total load for each cluster
        cluster_loads = []
        for cluster in clusters:
            total_load = sum(self.city_graph.bins[bin_id].current_fill for bin_id in cluster)
            cluster_loads.append((cluster, total_load))
            
        # Sort clusters by load in descending order
        cluster_loads.sort(key=lambda x: x[1], reverse=True)
        
        # Initialize truck assignments and their current loads
        truck_assignments = [[] for _ in range(num_trucks)]
        truck_loads = [0.0] * num_trucks
        
        # Distribute clusters using a greedy approach
        for cluster, load in cluster_loads:
            # Find truck with minimum current load
            min_load_truck = min(range(num_trucks), key=lambda i: truck_loads[i])
            truck_assignments[min_load_truck].append(cluster)
            truck_loads[min_load_truck] += load
            
        return truck_assignments
        
    def _optimize_route(self, bins: List[int]) -> Optional[Route]:
        """
        Optimize route for a given set of bins using dynamic programming.
        Returns None if no valid route is possible.
        """
        if not bins:
            return None
            
        n = len(bins)
        if n == 1:
            bin_data = self.city_graph.bins[bins[0]]
            return Route([bins[0]], 0, bin_data.current_fill, self.truck_capacity)
            
        # Create distance matrix
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    bin1 = self.city_graph.bins[bins[i]]
                    bin2 = self.city_graph.bins[bins[j]]
                    dist_matrix[i][j] = np.linalg.norm(
                        np.array(bin1.location) - np.array(bin2.location)
                    )
                    
        # Dynamic programming for TSP
        # dp[mask][last] represents minimum distance to visit subset of vertices represented by mask,
        # ending at vertex last
        dp = {}
        parent = {}
        
        def solve_tsp(mask: int, last: int) -> float:
            if mask == (1 << n) - 1:  # All vertices visited
                return 0
                
            state = (mask, last)
            if state in dp:
                return dp[state]
                
            min_dist = float('inf')
            best_next = -1
            
            for next_vertex in range(n):
                if not (mask & (1 << next_vertex)):  # If next_vertex not visited
                    new_dist = dist_matrix[last][next_vertex] + solve_tsp(
                        mask | (1 << next_vertex), next_vertex
                    )
                    if new_dist < min_dist:
                        min_dist = new_dist
                        best_next = next_vertex
                        
            dp[state] = min_dist
            parent[state] = best_next
            return min_dist
            
        # Find optimal route
        start_vertex = 0
        min_distance = solve_tsp(1 << start_vertex, start_vertex)
        
        # Reconstruct the path
        path = [start_vertex]
        mask = 1 << start_vertex
        last = start_vertex
        
        while len(path) < n:
            next_vertex = parent[(mask, last)]
            path.append(next_vertex)
            mask |= 1 << next_vertex
            last = next_vertex
            
        # Convert vertex indices back to bin IDs
        bin_sequence = [bins[i] for i in path]
        
        # Calculate total collection
        total_collection = sum(self.city_graph.bins[bin_id].current_fill 
                             for bin_id in bin_sequence)
                             
        if total_collection <= self.truck_capacity:
            return Route(bin_sequence, min_distance, total_collection, self.truck_capacity)
        return None
        
    def display_routes(self):
        """Display all planned routes in a formatted way."""
        if not self.routes:
            print("No routes planned.")
            return
            
        for i, route in enumerate(self.routes, 1):
            print(f"\nRoute {i}:")
            print("=" * 40)
            
            # Prepare route details
            details = []
            for bin_id in route.bin_sequence:
                bin_data = self.city_graph.bins[bin_id]
                details.append([
                    bin_id,
                    f"({bin_data.location[0]:.1f}, {bin_data.location[1]:.1f})",
                    f"{bin_data.current_fill:.1f}",
                    f"{bin_data.priority:.2f}"
                ])
                
            headers = ["Bin ID", "Location", "Collection Amount", "Priority"]
            print(tabulate(details, headers=headers, tablefmt="grid"))
            
            print(f"\nTotal Distance: {route.total_distance:.2f}")
            print(f"Total Collection: {route.total_collection:.2f}/{route.truck_capacity:.2f}")
            print("=" * 40) 