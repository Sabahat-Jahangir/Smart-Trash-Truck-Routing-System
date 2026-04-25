from typing import List, Tuple, Dict, Set
import networkx as nx
from dataclasses import dataclass
import numpy as np

@dataclass
class MSTRoute:
    edges: List[Tuple[str, str]]
    total_distance: float
    bins_served: Set[str]
    priority_score: float

class MSTOptimizer:
    def __init__(self, city_graph: nx.Graph):
        self.city_graph = city_graph
        self.mst_routes: List[MSTRoute] = []
        
    def optimize_routes(self, max_route_distance: float = 1000.0) -> List[MSTRoute]:
        """
        Optimizes routes using Kruskal's algorithm with modifications for capacity constraints.
        """
        # Get all bins and their fill levels
        bins = [(node, data) for node, data in self.city_graph.nodes(data=True)
                if data.get('type') == 'bin']
        
        # Sort bins by fill level (priority)
        bins.sort(key=lambda x: x[1]['fill_level'], reverse=True)
        
        routes = []
        unserved_bins = set(node for node, _ in bins)
        
        while unserved_bins:
            route = self._create_optimal_route(unserved_bins, max_route_distance)
            if not route:
                break
            routes.append(route)
            unserved_bins -= route.bins_served
            
        self.mst_routes = routes
        return routes
    
    def _create_optimal_route(self, available_bins: Set[str], 
                            max_distance: float) -> MSTRoute:
        """
        Creates an optimal route using Kruskal's algorithm with constraints.
        """
        if not available_bins:
            return None
            
        # Create subgraph with available bins
        subgraph = self.city_graph.subgraph(available_bins)
        
        # Get all edges with weights
        edges = [(u, v, data['weight']) 
                for u, v, data in subgraph.edges(data=True)]
        
        # Sort edges by weight
        edges.sort(key=lambda x: x[2])
        
        # Initialize disjoint set for Kruskal's algorithm
        parent = {node: node for node in subgraph.nodes()}
        rank = {node: 0 for node in subgraph.nodes()}
        
        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]
        
        def union(u, v):
            root_u, root_v = find(u), find(v)
            if root_u != root_v:
                if rank[root_u] < rank[root_v]:
                    root_u, root_v = root_v, root_u
                parent[root_v] = root_u
                if rank[root_u] == rank[root_v]:
                    rank[root_u] += 1
        
        # Apply Kruskal's algorithm with distance constraint
        mst_edges = []
        total_distance = 0
        bins_served = set()
        
        for u, v, weight in edges:
            if find(u) != find(v) and total_distance + weight <= max_distance:
                union(u, v)
                mst_edges.append((u, v))
                total_distance += weight
                bins_served.add(u)
                bins_served.add(v)
        
        if not mst_edges:
            return None
            
        # Calculate priority score based on fill levels
        priority_score = sum(self.city_graph.nodes[bin]['fill_level'] 
                           for bin in bins_served)
        
        return MSTRoute(
            edges=mst_edges,
            total_distance=total_distance,
            bins_served=bins_served,
            priority_score=priority_score
        )
    
    def get_route_stats(self) -> Dict:
        """
        Returns statistics about the optimized routes.
        """
        if not self.mst_routes:
            return {}
            
        return {
            'num_routes': len(self.mst_routes),
            'avg_distance': np.mean([r.total_distance for r in self.mst_routes]),
            'avg_bins_per_route': np.mean([len(r.bins_served) for r in self.mst_routes]),
            'total_priority_score': sum(r.priority_score for r in self.mst_routes),
            'total_bins_served': sum(len(r.bins_served) for r in self.mst_routes)
        } 