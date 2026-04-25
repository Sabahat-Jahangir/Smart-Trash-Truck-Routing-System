import networkx as nx
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from tabulate import tabulate

@dataclass
class Bin:
    id: int
    location: Tuple[float, float]  # (x, y) coordinates
    capacity: float
    current_fill: float
    priority: float  # 0-1 scale, 1 being highest priority
    
    @property
    def fill_percentage(self) -> float:
        return (self.current_fill / self.capacity) * 100
        
    @property
    def is_high_priority(self) -> bool:
        return self.priority > 0.7 or self.fill_percentage > 80

class CityGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.bins: Dict[int, Bin] = {}
        self.mst = None  # Minimum Spanning Tree
        
    def add_bin(self, bin_id: int, x: float, y: float, capacity: float, 
                current_fill: float = 0.0, priority: float = 0.0):
        """Add a bin to the city graph."""
        self.bins[bin_id] = Bin(
            id=bin_id,
            location=(x, y),
            capacity=capacity,
            current_fill=current_fill,
            priority=priority
        )
        self.graph.add_node(bin_id, pos=(x, y))
        
    def add_road(self, bin1_id: int, bin2_id: int, distance: float):
        """Add a road (edge) between two bins."""
        if bin1_id in self.bins and bin2_id in self.bins:
            self.graph.add_edge(bin1_id, bin2_id, weight=distance)
            
    def calculate_mst(self):
        """Calculate Minimum Spanning Tree using Kruskal's algorithm."""
        if not self.graph.edges():
            return
            
        self.mst = nx.minimum_spanning_tree(self.graph)
        
    def get_bin_clusters(self, max_distance: float) -> List[List[int]]:
        """
        Identify clusters of bins using adapted Kadane's algorithm concept.
        Returns lists of bin IDs representing clusters.
        """
        if not self.bins:
            return []
            
        # Convert bins to numpy array for efficient computation
        points = np.array([bin.location for bin in self.bins.values()])
        n = len(points)
        clusters = []
        visited = set()
        
        for i in range(n):
            if i in visited:
                continue
                
            cluster = [i]
            visited.add(i)
            
            # Find all points within max_distance of current point
            for j in range(i + 1, n):
                if j in visited:
                    continue
                    
                dist = np.linalg.norm(points[i] - points[j])
                if dist <= max_distance:
                    cluster.append(j)
                    visited.add(j)
                    
            if len(cluster) > 1:  # Only add clusters with more than one bin
                clusters.append([list(self.bins.keys())[i] for i in cluster])
                
        return clusters
        
    def update_bin_fill_level(self, bin_id: int, new_fill: float):
        """Update the fill level of a bin."""
        if bin_id in self.bins:
            self.bins[bin_id].current_fill = min(new_fill, self.bins[bin_id].capacity)
            self.bins[bin_id].priority = self.bins[bin_id].fill_percentage / 100
            
    def get_high_priority_bins(self) -> List[int]:
        """Get list of high priority bin IDs."""
        return [bin_id for bin_id, bin in self.bins.items() if bin.is_high_priority]
        
    def display_status(self):
        """Display current status of all bins in a formatted table."""
        if not self.bins:
            print("No bins in the system.")
            return
            
        headers = ["Bin ID", "Location", "Capacity", "Current Fill", "Fill %", "Priority"]
        rows = []
        
        for bin_id, bin in sorted(self.bins.items()):
            rows.append([
                bin_id,
                f"({bin.location[0]:.1f}, {bin.location[1]:.1f})",
                f"{bin.capacity:.1f}",
                f"{bin.current_fill:.1f}",
                f"{bin.fill_percentage:.1f}%",
                f"{bin.priority:.2f}"
            ])
            
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        
    def get_nearest_neighbors(self, bin_id: int, k: int = 5) -> List[Tuple[int, float]]:
        """Get k nearest neighbors of a bin."""
        if bin_id not in self.bins:
            return []
            
        distances = []
        source = self.bins[bin_id].location
        
        for other_id, other_bin in self.bins.items():
            if other_id != bin_id:
                dist = np.linalg.norm(
                    np.array(source) - np.array(other_bin.location)
                )
                distances.append((other_id, dist))
                
        return sorted(distances, key=lambda x: x[1])[:k] 