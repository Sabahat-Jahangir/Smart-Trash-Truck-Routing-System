import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict
import networkx as nx

@dataclass
class ClusterMetrics:
    center: Tuple[float, float]
    bins: List[str]
    total_weight: float
    radius: float
    density: float

class ClusterAnalyzer:
    def __init__(self, city_graph: nx.Graph):
        self.city_graph = city_graph
        self.clusters: List[ClusterMetrics] = []
        
    def find_optimal_clusters(self, min_density: float = 0.5) -> List[ClusterMetrics]:
        """
        Finds optimal clusters using an adaptation of Kadane's algorithm for 2D space.
        Uses bin fill levels as weights for clustering.
        """
        bins = [(data['pos'], node, data['fill_level']) 
                for node, data in self.city_graph.nodes(data=True)
                if data.get('type') == 'bin']
        
        if not bins:
            return []
            
        # Sort bins by x-coordinate for sweep line approach
        bins.sort(key=lambda x: x[0][0])
        
        best_clusters = []
        current_cluster = []
        current_sum = 0
        
        for pos, node_id, fill_level in bins:
            # Calculate density contribution
            density_contribution = self._calculate_density_contribution(pos, current_cluster)
            
            if current_sum + fill_level * density_contribution > 0:
                current_cluster.append((pos, node_id, fill_level))
                current_sum += fill_level * density_contribution
            else:
                if current_cluster:
                    cluster_metrics = self._create_cluster_metrics(current_cluster)
                    if cluster_metrics.density >= min_density:
                        best_clusters.append(cluster_metrics)
                current_cluster = [(pos, node_id, fill_level)]
                current_sum = fill_level
        
        # Handle the last cluster
        if current_cluster:
            cluster_metrics = self._create_cluster_metrics(current_cluster)
            if cluster_metrics.density >= min_density:
                best_clusters.append(cluster_metrics)
        
        self.clusters = best_clusters
        return best_clusters
    
    def _calculate_density_contribution(self, new_pos: Tuple[float, float], 
                                     cluster: List[Tuple]) -> float:
        """
        Calculates how much a new bin would contribute to cluster density.
        """
        if not cluster:
            return 1.0
            
        # Calculate average distance to existing cluster points
        distances = [self._euclidean_distance(new_pos, pos) 
                    for pos, _, _ in cluster]
        avg_distance = np.mean(distances)
        
        # Normalize to (0, 1] range using exponential decay
        return np.exp(-avg_distance / 100)  # 100 is a scaling factor
    
    def _create_cluster_metrics(self, cluster: List[Tuple]) -> ClusterMetrics:
        """
        Creates metrics for a cluster including its center, total weight, and density.
        """
        positions = np.array([pos for pos, _, _ in cluster])
        weights = np.array([w for _, _, w in cluster])
        
        # Calculate weighted center
        center = tuple(np.average(positions, weights=weights, axis=0))
        
        # Calculate radius as max distance from center
        radius = max(self._euclidean_distance(center, pos) for pos, _, _ in cluster)
        
        # Calculate density as total weight / area
        area = np.pi * radius ** 2 if radius > 0 else 1
        density = sum(weights) / area
        
        return ClusterMetrics(
            center=center,
            bins=[node_id for _, node_id, _ in cluster],
            total_weight=sum(weights),
            radius=radius,
            density=density
        )
    
    @staticmethod
    def _euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def get_cluster_stats(self) -> Dict:
        """
        Returns statistics about the clusters.
        """
        if not self.clusters:
            return {}
            
        return {
            'num_clusters': len(self.clusters),
            'avg_bins_per_cluster': np.mean([len(c.bins) for c in self.clusters]),
            'avg_density': np.mean([c.density for c in self.clusters]),
            'total_bins': sum(len(c.bins) for c in self.clusters),
            'avg_radius': np.mean([c.radius for c in self.clusters])
        } 