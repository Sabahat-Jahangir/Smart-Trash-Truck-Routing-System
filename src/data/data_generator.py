import random
import networkx as nx
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from .data_manager import DataManager, BinRecord, RouteRecord

class DataGenerator:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.city_sizes = {
            'small': (5, 10, 20),   # (bins, intersections, edges)
            'medium': (15, 25, 50),
            'large': (30, 50, 100)
        }
        
    def generate_city_data(self, size: str = 'medium', seed: int = None) -> nx.Graph:
        """Generate a city graph with the specified size."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        num_bins, num_intersections, num_edges = self.city_sizes.get(
            size, self.city_sizes['medium'])
            
        # Create graph
        G = nx.Graph()
        
        # Generate positions for all nodes
        positions = self._generate_positions(num_bins + num_intersections)
        
        # Add intersections
        for i in range(num_intersections):
            node_id = f"i{i}"
            G.add_node(node_id, 
                      pos=positions[i],
                      type='intersection')
        
        # Add bins with random fill levels
        for i in range(num_bins):
            node_id = f"b{i}"
            fill_level = random.uniform(0.1, 1.0)
            pos = positions[num_intersections + i]
            
            G.add_node(node_id,
                      pos=pos,
                      type='bin',
                      fill_level=fill_level)
            
            # Create and save bin record
            bin_record = BinRecord(
                bin_id=node_id,
                location=pos,
                fill_level=fill_level,
                last_collection=self._get_random_past_date(),
                collection_history=[]
            )
            self.data_manager.update_bin(bin_record)
        
        # Add edges with weights (distances)
        edges = self._generate_edges(G, num_edges)
        for u, v in edges:
            weight = self._calculate_edge_weight(G, u, v)
            G.add_edge(u, v, weight=weight)
        
        return G
    
    def _generate_positions(self, num_nodes: int) -> List[Tuple[float, float]]:
        """Generate random positions for nodes."""
        positions = []
        min_distance = 0.1  # Minimum distance between nodes
        
        while len(positions) < num_nodes:
            x = random.uniform(0, 10)
            y = random.uniform(0, 10)
            new_pos = (x, y)
            
            # Check minimum distance from existing positions
            if all(self._euclidean_distance(new_pos, pos) >= min_distance 
                   for pos in positions):
                positions.append(new_pos)
        
        return positions
    
    def _generate_edges(self, G: nx.Graph, num_edges: int) -> List[Tuple[str, str]]:
        """Generate edges ensuring connectivity."""
        nodes = list(G.nodes())
        
        # First, create a minimum spanning tree to ensure connectivity
        tree_edges = []
        connected = {nodes[0]}
        unconnected = set(nodes[1:])
        
        while unconnected:
            best_edge = None
            best_weight = float('inf')
            
            for u in connected:
                for v in unconnected:
                    weight = self._calculate_edge_weight(G, u, v)
                    if weight < best_weight:
                        best_edge = (u, v)
                        best_weight = weight
            
            if best_edge:
                u, v = best_edge
                tree_edges.append(best_edge)
                connected.add(v)
                unconnected.remove(v)
        
        # Add remaining random edges
        possible_edges = [(u, v) for u in nodes for v in nodes 
                         if u < v and (u, v) not in tree_edges]
        random_edges = random.sample(possible_edges, 
                                   min(num_edges - len(tree_edges), 
                                       len(possible_edges)))
        
        return tree_edges + random_edges
    
    def _calculate_edge_weight(self, G: nx.Graph, u: str, v: str) -> float:
        """Calculate the weight (distance) between two nodes."""
        pos_u = G.nodes[u]['pos']
        pos_v = G.nodes[v]['pos']
        return self._euclidean_distance(pos_u, pos_v)
    
    @staticmethod
    def _euclidean_distance(p1: Tuple[float, float], 
                           p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def _get_random_past_date() -> str:
        """Generate a random date within the last 30 days."""
        days_ago = random.randint(0, 30)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    
    def update_fill_levels(self, G: nx.Graph, time_factor: float = 1.0):
        """Update bin fill levels based on time passage."""
        for node in G.nodes():
            if G.nodes[node]['type'] == 'bin':
                bin_record = self.data_manager.get_bin(node)
                if bin_record:
                    # Calculate new fill level
                    fill_rate = random.uniform(0.01, 0.05) * time_factor
                    new_fill = min(1.0, bin_record.fill_level + fill_rate)
                    
                    # Update both graph and persistent storage
                    G.nodes[node]['fill_level'] = new_fill
                    bin_record.fill_level = new_fill
                    self.data_manager.update_bin(bin_record)
    
    def record_collection(self, route_id: str, bins_served: List[str], 
                         total_distance: float, collection_amount: float):
        """Record a completed collection route."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create route record
        route_record = RouteRecord(
            route_id=route_id,
            timestamp=timestamp,
            bins_served=bins_served,
            total_distance=total_distance,
            priority_score=sum(self.data_manager.get_bin(bin_id).fill_level 
                             for bin_id in bins_served),
            collection_amount=collection_amount
        )
        
        # Add route record
        self.data_manager.add_route_record(route_record)
        
        # Update bin records
        for bin_id in bins_served:
            bin_record = self.data_manager.get_bin(bin_id)
            if bin_record:
                bin_record.last_collection = timestamp
                bin_record.fill_level = 0.0  # Reset fill level after collection
                bin_record.collection_history.append({
                    "timestamp": timestamp,
                    "amount_collected": collection_amount / len(bins_served)
                })
                self.data_manager.update_bin(bin_record) 