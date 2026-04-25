import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
from typing import List, Dict, Optional, Union
from src.models.city_graph import CityGraph
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

class VisualizationManager:
    """Unified visualization manager for the Smart Trash Truck Routing System."""
    
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = output_dir
        self.style_config = {
            'dpi': 300,
            'figsize': (12, 8),
            'cmap': 'viridis',
            'node_size': 500,
            'edge_width': 2,
            'font_size': 10,
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
        }
        self._create_output_dirs()
        
    def _create_output_dirs(self):
        """Create necessary directories for different visualization formats."""
        subdirs = ['png', 'pdf', 'svg', 'city_graph', 'routes', 'clusters', 'metrics']
        for subdir in subdirs:
            path = os.path.join(self.output_dir, subdir)
            os.makedirs(path, exist_ok=True)
            
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _save_plot(self, fig, name: str, subdir: str = None, formats: List[str] = None):
        """Save plot in multiple formats."""
        if formats is None:
            formats = ['png', 'pdf', 'svg']
            
        timestamp = self._get_timestamp()
        base_name = f"{name}_{timestamp}"
        
        for fmt in formats:
            save_path = os.path.join(self.output_dir, fmt)
            if subdir:
                save_path = os.path.join(save_path, subdir)
            os.makedirs(save_path, exist_ok=True)
            
            full_path = os.path.join(save_path, f"{base_name}.{fmt}")
            if fmt == 'png':
                fig.savefig(full_path, dpi=self.style_config['dpi'], bbox_inches='tight')
            else:
                fig.savefig(full_path, bbox_inches='tight')
                
    def plot_city_graph(self, city_graph: CityGraph, 
                       highlight_nodes: Optional[List[str]] = None,
                       show_labels: bool = True,
                       save: bool = True):
        """Plot the city graph with enhanced styling and optional node highlighting."""
        fig, ax = plt.subplots(figsize=self.style_config['figsize'])
        G = city_graph.graph
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw base graph
        nx.draw_networkx_edges(G, pos, alpha=0.2, 
                             width=self.style_config['edge_width'])
        
        # Prepare node colors based on fill levels
        node_colors = []
        for node in G.nodes():
            bin_data = city_graph.bins[node]
            fill_percentage = bin_data.fill_percentage
            if fill_percentage > 80:
                color = '#FF0000'  # Red for high priority
            elif fill_percentage > 50:
                color = '#FFA500'  # Orange for medium
            else:
                color = '#00FF00'  # Green for low
            node_colors.append(color)
            
        # Draw nodes with highlighting if specified
        if highlight_nodes:
            node_sizes = [
                self.style_config['node_size'] * 1.5 if node in highlight_nodes
                else self.style_config['node_size']
                for node in G.nodes()
            ]
        else:
            node_sizes = [self.style_config['node_size']] * len(G.nodes())
            
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                             node_size=node_sizes,
                             edgecolors='black', linewidths=1)
        
        if show_labels:
            labels = {node: f"Bin {node}\n{city_graph.bins[node].fill_percentage:.0f}%" 
                     for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, 
                                  font_size=self.style_config['font_size'])
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF0000',
                      label='High Fill (>80%)', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFA500',
                      label='Medium Fill (>50%)', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00FF00',
                      label='Low Fill', markersize=10)
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title("City Graph - Bin Locations and Fill Levels", pad=20, 
                 fontsize=14)
        plt.axis('equal')
        
        if save:
            self._save_plot(fig, 'city_graph', 'city_graph')
            plt.close()
        else:
            plt.show()
            
    def plot_routes(self, city_graph: CityGraph, routes: List[Dict],
                   show_labels: bool = True, save: bool = True):
        """Plot planned routes with enhanced styling and statistics."""
        fig, ax = plt.subplots(figsize=self.style_config['figsize'])
        G = city_graph.graph
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw base graph
        nx.draw_networkx_edges(G, pos, alpha=0.1, 
                             width=self.style_config['edge_width'])
        
        # Draw routes
        for i, route in enumerate(routes):
            color = self.style_config['colors'][i % len(self.style_config['colors'])]
            path_edges = list(zip(route['bins_served'][:-1], route['bins_served'][1:]))
            
            # Draw route edges with arrows
            nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                                 edge_color=color,
                                 width=self.style_config['edge_width'],
                                 arrowsize=20, arrowstyle='->')
            
            # Draw nodes in route
            nx.draw_networkx_nodes(G, pos, nodelist=route['bins_served'],
                                 node_color=color,
                                 node_size=self.style_config['node_size'],
                                 edgecolors='black', linewidths=1)
            
            # Add route statistics
            start_pos = pos[route['bins_served'][0]]
            plt.annotate(
                f"Route {route['route_id']}\n"
                f"Distance: {route['total_distance']:.1f} km\n"
                f"Collection: {route['collection_amount']:.1f} tons",
                start_pos,
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(facecolor='white', edgecolor=color, alpha=0.8),
                fontsize=self.style_config['font_size']
            )
            
        if show_labels:
            labels = {node: f"Bin {node}" for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels,
                                  font_size=self.style_config['font_size'])
            
        plt.title("Planned Routes for Trash Collection", pad=20, fontsize=14)
        plt.axis('equal')
        
        if save:
            self._save_plot(fig, 'routes', 'routes')
            plt.close()
        else:
            plt.show()
            
    def plot_route_comparison(self, city_graph: CityGraph,
                            original_routes: List[Dict],
                            optimized_routes: List[Dict],
                            show_labels: bool = True,
                            save: bool = True):
        """Plot comparison between original and optimized routes."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        G = city_graph.graph
        pos = nx.get_node_attributes(G, 'pos')
        
        for ax, routes, title in [(ax1, original_routes, "Original Routes"),
                                (ax2, optimized_routes, "Optimized Routes")]:
            plt.sca(ax)
            
            # Draw base graph
            nx.draw_networkx_edges(G, pos, alpha=0.1,
                                 width=self.style_config['edge_width'])
            
            # Draw routes
            for i, route in enumerate(routes):
                color = self.style_config['colors'][i % len(self.style_config['colors'])]
                path_edges = list(zip(route['bins_served'][:-1], route['bins_served'][1:]))
                
                nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                                     edge_color=color,
                                     width=self.style_config['edge_width'],
                                     arrowsize=20, arrowstyle='->')
                
                nx.draw_networkx_nodes(G, pos, nodelist=route['bins_served'],
                                     node_color=color,
                                     node_size=self.style_config['node_size'],
                                     edgecolors='black', linewidths=1)
                                     
            if show_labels:
                labels = {node: f"Bin {node}" for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels,
                                      font_size=self.style_config['font_size'])
                                      
            plt.title(title, pad=20, fontsize=14)
            plt.axis('equal')
            
        # Add overall statistics
        orig_dist = sum(r['total_distance'] for r in original_routes)
        opt_dist = sum(r['total_distance'] for r in optimized_routes)
        improvement = ((orig_dist - opt_dist) / orig_dist) * 100
        
        fig.suptitle(
            f"Route Optimization Comparison\n"
            f"Total Distance: {orig_dist:.1f} km → {opt_dist:.1f} km\n"
            f"Improvement: {improvement:.1f}%",
            fontsize=16, y=1.05
        )
        
        if save:
            self._save_plot(fig, 'route_comparison', 'routes')
            plt.close()
        else:
            plt.show()
            
    def plot_metrics(self, routes: List[Dict], save: bool = True):
        """Plot comprehensive performance metrics for routes."""
        fig = plt.figure(figsize=(15, 10))
        
        # Route distances
        plt.subplot(221)
        distances = [route['total_distance'] for route in routes]
        bars = plt.bar(range(1, len(routes) + 1), distances,
                      color=self.style_config['colors'])
        plt.title('Total Distance per Route', pad=10, fontsize=12)
        plt.xlabel('Route Number')
        plt.ylabel('Distance (km)')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
                    
        # Collections vs Capacity
        plt.subplot(222)
        collections = [route['collection_amount'] for route in routes]
        x = range(1, len(routes) + 1)
        bars = plt.bar(x, collections,
                      color=self.style_config['colors'])
        plt.title('Collection Amount per Route', pad=10, fontsize=12)
        plt.xlabel('Route Number')
        plt.ylabel('Collection Amount (tons)')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
                    
        # Efficiency ratio
        plt.subplot(223)
        efficiency = [route['collection_amount']/route['total_distance'] 
                     for route in routes]
        bars = plt.bar(range(1, len(routes) + 1), efficiency,
                      color=self.style_config['colors'])
        plt.title('Collection Efficiency (tons/km)', pad=10, fontsize=12)
        plt.xlabel('Route Number')
        plt.ylabel('Efficiency')
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
                    
        # Time distribution
        plt.subplot(224)
        timestamps = [datetime.strptime(route['timestamp'], "%Y%m%d_%H%M%S") 
                     for route in routes]
        plt.hist(timestamps, bins=min(len(routes), 10),
                color=self.style_config['colors'][0])
        plt.title('Route Timestamp Distribution', pad=10, fontsize=12)
        plt.xlabel('Time')
        plt.ylabel('Number of Routes')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save:
            self._save_plot(fig, 'route_metrics', 'metrics')
            plt.close()
        else:
            plt.show() 