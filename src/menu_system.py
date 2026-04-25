import time
import json
import os
from src.utils.terminal_utils import clear_screen, center_text, create_centered_menu
from src.models.city_graph import CityGraph
from src.models.route_planner import RoutePlanner
from src.data.data_generator import DataGenerator
from src.utils.visualization import Visualizer
from colorama import Fore, Style
from src.data.data_manager import DataManager
from src.models.cluster_analyzer import ClusterAnalyzer
from src.models.mst_optimizer import MSTOptimizer
from src.utils.visualization import VisualizationManager
import sys
from datetime import datetime

class MenuSystem:
    def __init__(self):
        try:
            # Initialize core components first
            self.data_manager = DataManager()
            self.data_generator = DataGenerator(self.data_manager)
            
            # Initialize visualization components
            self.visualizer = Visualizer()
            self.visualization_manager = VisualizationManager()  # Renamed for clarity
            
            # Initialize route planning components
            self.city_graph = None
            self.route_planner = None
            self.cluster_analyzer = None
            self.mst_optimizer = None
            
            # Initialize menu state
            self.menu_history = []
            self.settings = self._load_default_settings()
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
        except Exception as e:
            print(f"Error initializing MenuSystem: {str(e)}")
            sys.exit(1)
            
    def _load_default_settings(self):
        """Load default system settings."""
        return {
            'truck_capacity': 1000.0,
            'max_cluster_distance': 50.0,
            'num_trucks': 1,
            'visualization': {
                'show_labels': True,
                'map_style': 'default',
                'save_format': 'png'
            },
            'routing': {
                'optimization_method': 'mst',
                'max_route_length': 100.0,
                'min_fill_level': 0.5
            }
        }
        
    def _initialize_route_components(self):
        """Initialize route planning components if city data is available."""
        if not self.city_graph:
            return False
            
        try:
            self.route_planner = RoutePlanner(
                city_graph=self.city_graph,
                settings=self.settings['routing']
            )
            self.cluster_analyzer = ClusterAnalyzer(
                city_graph=self.city_graph,
                max_distance=self.settings['max_cluster_distance']
            )
            self.mst_optimizer = MSTOptimizer(
                city_graph=self.city_graph,
                settings=self.settings['routing']
            )
            return True
        except Exception as e:
            print(f"Error initializing route components: {str(e)}")
            return False
        
    def display_main_menu(self):
        """Display the main menu options."""
        print(center_text("1. Generate/Load City Data"))
        print(center_text("2. Plan Routes"))
        print(center_text("3. Analyze Clusters"))
        print(center_text("4. Visualize Data"))
        print(center_text("5. View Statistics"))
        print(center_text("6. Export/Import Data"))
        print(center_text("7. System Settings"))
        print(center_text("q. Quit"))
        
    def handle_main_menu_choice(self, choice: str):
        """Handle the user's main menu choice."""
        self.menu_history.append('main')
        
        if choice == '1':
            self.show_data_menu()
        elif choice == '2':
            self.show_route_menu()
        elif choice == '3':
            self.show_cluster_menu()
        elif choice == '4':
            self.show_visualization_menu()
        elif choice == '5':
            self.show_statistics_menu()
        elif choice == '6':
            self.show_data_management_menu()
        elif choice == '7':
            self.show_settings_menu()
        elif choice == 'q':
            print(center_text("Goodbye!"))
            sys.exit(0)
        else:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def go_back(self):
        """Return to the previous menu."""
        if self.menu_history:
            self.menu_history.pop()
            if self.menu_history:
                last_menu = self.menu_history[-1]
                self._display_menu(last_menu)
            else:
                self.display_main_menu()
                
    def show_data_menu(self):
        """Show data generation and loading options."""
        while True:
            clear_screen()
            print(center_text("=== Data Management ==="))
            print(center_text("1. Generate New City (Small)"))
            print(center_text("2. Generate New City (Medium)"))
            print(center_text("3. Generate New City (Large)"))
            print(center_text("4. Load Saved City"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice in ['1', '2', '3']:
                size = {'1': 'small', '2': 'medium', '3': 'large'}[choice]
                self.city_graph = self.data_generator.generate_city_data(size)
                print(center_text(f"\nGenerated {size} city with "
                                f"{len(self.city_graph.nodes())} nodes"))
                time.sleep(2)
            elif choice == '4':
                # Implement loading saved city
                pass
                
    def show_route_menu(self):
        """Show route planning options."""
        if not self.city_graph:
            print(center_text("\nPlease generate or load city data first!"))
            time.sleep(2)
            return
            
        while True:
            clear_screen()
            print(center_text("=== Route Planning ==="))
            print(center_text("1. Plan New Routes"))
            print(center_text("2. View Current Routes"))
            print(center_text("3. Optimize Routes"))
            print(center_text("4. Save Routes"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                self._plan_new_routes()
            elif choice == '2':
                self.view_routes()
            elif choice == '3':
                self.optimize_routes()
            elif choice == '4':
                self.save_routes()
                
    def show_cluster_menu(self):
        """Show cluster analysis options."""
        if not self.city_graph:
            print(center_text("\nPlease generate or load city data first!"))
            time.sleep(2)
            return
            
        while True:
            clear_screen()
            print(center_text("=== Cluster Analysis ==="))
            print(center_text("1. Analyze Clusters"))
            print(center_text("2. View Cluster Statistics"))
            print(center_text("3. Export Cluster Data"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                self.analyze_clusters()
            elif choice == '2':
                self.view_cluster_stats()
            elif choice == '3':
                self.export_cluster_data()
                
    def show_visualization_menu(self):
        """Show visualization options."""
        if not self.city_graph:
            print(center_text("\nPlease generate or load city data first!"))
            time.sleep(2)
            return
            
        while True:
            clear_screen()
            print(center_text("=== Visualization ==="))
            print(center_text("1. View City Graph"))
            print(center_text("2. View Routes"))
            print(center_text("3. View Clusters"))
            print(center_text("4. View Performance Metrics"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                self.visualizer.plot_city_graph(self.city_graph, save=False)
            elif choice == '2':
                self.view_route_visualization()
            elif choice == '3':
                self.view_cluster_visualization()
            elif choice == '4':
                self.view_performance_visualization()
                
    def show_statistics_menu(self):
        """Show system statistics."""
        while True:
            clear_screen()
            print(center_text("=== System Statistics ==="))
            
            stats = self.data_manager.get_system_stats()
            print(center_text(f"Total Collections: {stats['total_collections']}"))
            print(center_text(f"Total Distance: {stats['total_distance']:.2f} km"))
            print(center_text(f"Total Waste Collected: {stats['total_waste_collected']:.2f} tons"))
            
            print(center_text("\nPress 'b' to go back"))
            if input().strip().lower() == 'b':
                break
                
    def show_data_management_menu(self):
        """Show data export/import options."""
        while True:
            clear_screen()
            print(center_text("=== Data Management ==="))
            print(center_text("1. Export All Data"))
            print(center_text("2. Import Data"))
            print(center_text("3. Clear All Data"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                export_path = self.data_manager.export_data()
                print(center_text(f"\nData exported to: {export_path}"))
                time.sleep(2)
            elif choice == '2':
                path = input("\nEnter import directory path: ").strip()
                if self.data_manager.import_data(path):
                    print(center_text("\nData imported successfully!"))
                else:
                    print(center_text("\nError importing data!"))
                time.sleep(2)
            elif choice == '3':
                confirm = input("\nAre you sure? This will delete all data! (y/n): ").strip().lower()
                if confirm == 'y':
                    self.data_manager.clear_data()
                    print(center_text("\nAll data cleared!"))
                    time.sleep(2)
                    
    def show_settings_menu(self):
        """Show system settings options."""
        while True:
            clear_screen()
            print(center_text("=== System Settings ==="))
            print(center_text("1. Update Visualization Settings"))
            print(center_text("2. Update Route Planning Parameters"))
            print(center_text("3. Update Clustering Parameters"))
            print(center_text("b. Back to Main Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            # Implement other settings options
            
    def _handle_generate_data(self):
        clear_screen()
        print(center_text("=== Generate Sample Data ==="))
        print("\n")
        
        options = [
            "1. Small Dataset (5-7 bins)",
            "2. Medium Dataset (10-15 bins)",
            "3. Large Dataset (20+ bins)",
            "B. Back to Main Menu"
        ]
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        try:
            size = {
                '1': 'small',
                '2': 'medium',
                '3': 'large'
            }[choice]
            
            self.city_graph = self.data_generator.generate_city_data(size)
            self.route_planner = RoutePlanner(self.city_graph)
            
            print(center_text("Sample data generated successfully!"))
            time.sleep(1.5)
            
        except KeyError:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def _handle_load_data(self):
        clear_screen()
        print(center_text("=== Load Existing Data ==="))
        print("\n")
        
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            print(center_text("No saved data found."))
            time.sleep(1.5)
            return
            
        # List all .json files in the data directory
        saved_files = [f for f in os.listdir('data') if f.endswith('.json')]
        
        if not saved_files:
            print(center_text("No saved data found."))
            time.sleep(1.5)
            return
            
        print(center_text("Available Data Files:"))
        print("\n")
        
        options = [f"{i+1}. {file}" for i, file in enumerate(saved_files)]
        options.append("B. Back to Main Menu")
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(saved_files):
                self._load_data_file(saved_files[file_index])
            else:
                raise ValueError
                
        except ValueError:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def _load_data_file(self, filename: str):
        """Load city data from a JSON file."""
        try:
            with open(os.path.join('data', filename), 'r') as f:
                data = json.load(f)
                
            # Create new CityGraph
            self.city_graph = CityGraph()
            
            # Load bins
            for bin_data in data['bins']:
                self.city_graph.add_bin(
                    bin_id=bin_data['id'],
                    x=bin_data['location'][0],
                    y=bin_data['location'][1],
                    capacity=bin_data['capacity'],
                    current_fill=bin_data['current_fill'],
                    priority=bin_data['priority']
                )
                
            # Load roads
            for road in data['roads']:
                self.city_graph.add_road(
                    bin1_id=road['bin1'],
                    bin2_id=road['bin2'],
                    distance=road['distance']
                )
                
            # Initialize route planner
            self.route_planner = RoutePlanner(self.city_graph)
            
            print(center_text("\nData loaded successfully!"))
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(center_text(f"\nError loading data: {str(e)}"))
            
        time.sleep(1.5)
        
    def _save_current_data(self):
        """Save current city data to a JSON file."""
        if not self.city_graph:
            print(center_text("No data to save."))
            time.sleep(1.5)
            return
            
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
                
            # Prepare data for saving
            data = {
                'bins': [],
                'roads': []
            }
            
            # Save bins
            for bin_id, bin_obj in self.city_graph.bins.items():
                data['bins'].append({
                    'id': bin_id,
                    'location': list(bin_obj.location),
                    'capacity': bin_obj.capacity,
                    'current_fill': bin_obj.current_fill,
                    'priority': bin_obj.priority
                })
                
            # Save roads
            for (bin1, bin2, attrs) in self.city_graph.graph.edges(data=True):
                data['roads'].append({
                    'bin1': bin1,
                    'bin2': bin2,
                    'distance': attrs['weight']
                })
                
            # Generate filename with timestamp
            filename = f"city_data_{int(time.time())}.json"
            
            with open(os.path.join('data', filename), 'w') as f:
                json.dump(data, f, indent=2)
                
            print(center_text(f"\nData saved successfully as {filename}"))
            
        except Exception as e:
            print(center_text(f"\nError saving data: {str(e)}"))
            
        time.sleep(1.5)
        
    def _handle_system_status(self):
        if not self.city_graph:
            print(center_text("No data loaded. Please generate or load data first."))
            time.sleep(1.5)
            return
            
        clear_screen()
        print(center_text("=== System Status ==="))
        print("\n")
        self.city_graph.display_status()
        
        input(center_text("Press Enter to continue..."))
        
    def _handle_plan_routes(self):
        if not self.route_planner:
            print(center_text("No data loaded. Please generate or load data first."))
            time.sleep(1.5)
            return
            
        clear_screen()
        print(center_text("=== Route Planning ==="))
        print("\n")
        
        options = [
            "1. Plan New Routes",
            "2. Optimize Existing Routes",
            "3. View Route Statistics",
            "4. Configure Route Parameters",
            "B. Back to Main Menu"
        ]
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        if choice == '1':
            self._plan_new_routes()
        elif choice == '2':
            self._optimize_routes()
        elif choice == '3':
            self._view_route_stats()
        elif choice == '4':
            self._configure_route_params()
        else:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def _plan_new_routes(self):
        """Plan new routes based on current city data and settings."""
        if not self.city_graph:
            print(center_text("\nPlease generate or load city data first!"))
            time.sleep(2)
            return False
            
        try:
            # Initialize components if needed
            if not self._initialize_route_components():
                print(center_text("\nFailed to initialize route planning components!"))
                time.sleep(2)
                return False
                
            # Get bins that need service (fill level above minimum threshold)
            bins_to_service = [
                bin_id for bin_id, data in self.data_manager.bins.items()
                if data['fill_level'] >= self.settings['routing']['min_fill_level']
            ]
            
            if not bins_to_service:
                print(center_text("\nNo bins currently need service!"))
                time.sleep(2)
                return False
                
            # Generate routes
            routes = self.route_planner.plan_routes(
                bins_to_service,
                self.settings['num_trucks'],
                self.settings['truck_capacity']
            )
            
            # Save routes
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data_manager.save_routes(routes, timestamp)
            
            # Generate visualizations
            self.visualization_manager.plot_routes(
                self.city_graph,
                routes,
                show_labels=self.settings['visualization']['show_labels']
            )
            
            print(center_text(f"\nSuccessfully planned {len(routes)} routes!"))
            time.sleep(2)
            return True
            
        except Exception as e:
            print(center_text(f"\nError planning routes: {str(e)}"))
            time.sleep(2)
            return False
            
    def optimize_routes(self):
        """Optimize existing routes using MST algorithm."""
        if not self.city_graph or not self.route_planner:
            print(center_text("\nPlease plan routes first!"))
            time.sleep(2)
            return False
            
        try:
            # Initialize optimizer if needed
            if not self.mst_optimizer:
                if not self._initialize_route_components():
                    print(center_text("\nFailed to initialize route optimizer!"))
                    time.sleep(2)
                    return False
                    
            # Get current routes
            current_routes = self.data_manager.routes
            if not current_routes:
                print(center_text("\nNo routes available to optimize!"))
                time.sleep(2)
                return False
                
            # Optimize routes
            optimized_routes = self.mst_optimizer.optimize_routes(current_routes)
            
            # Save optimized routes
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data_manager.save_routes(optimized_routes, timestamp)
            
            # Generate comparison visualization
            self.visualization_manager.plot_route_comparison(
                self.city_graph,
                current_routes,
                optimized_routes,
                show_labels=self.settings['visualization']['show_labels']
            )
            
            # Calculate improvement metrics
            old_distance = sum(r['total_distance'] for r in current_routes)
            new_distance = sum(r['total_distance'] for r in optimized_routes)
            improvement = ((old_distance - new_distance) / old_distance) * 100
            
            print(center_text(f"\nRoutes optimized! Distance reduced by {improvement:.1f}%"))
            time.sleep(2)
            return True
            
        except Exception as e:
            print(center_text(f"\nError optimizing routes: {str(e)}"))
            time.sleep(2)
            return False
            
    def view_routes(self):
        """Display current route information."""
        if not self.data_manager.routes:
            print(center_text("\nNo routes available to view!"))
            time.sleep(2)
            return
            
        while True:
            clear_screen()
            print(center_text("=== Current Routes ===\n"))
            
            # Group routes by timestamp
            routes_by_time = {}
            for route in self.data_manager.routes:
                timestamp = route['timestamp']
                if timestamp not in routes_by_time:
                    routes_by_time[timestamp] = []
                routes_by_time[timestamp].append(route)
                
            # Display route summaries
            for timestamp, routes in routes_by_time.items():
                print(center_text(f"Routes from {timestamp}:"))
                total_distance = sum(r['total_distance'] for r in routes)
                total_collection = sum(r['collection_amount'] for r in routes)
                print(center_text(f"Total Routes: {len(routes)}"))
                print(center_text(f"Total Distance: {total_distance:.1f} km"))
                print(center_text(f"Total Collection: {total_collection:.1f} tons\n"))
                
            print(center_text("1. View Route Details"))
            print(center_text("2. View Route Visualization"))
            print(center_text("b. Back to Route Menu"))
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                self._view_route_details()
            elif choice == '2':
                self._view_route_visualization()
                
    def _view_route_details(self):
        """Display detailed information for a specific route."""
        if not self.data_manager.routes:
            return
            
        while True:
            clear_screen()
            print(center_text("=== Route Details ===\n"))
            
            # List available routes
            for i, route in enumerate(self.data_manager.routes, 1):
                print(center_text(f"{i}. Route {route['route_id']} ({route['timestamp']})"))
            print(center_text("b. Back"))
            
            choice = input("\nSelect a route to view (or 'b' to go back): ").strip().lower()
            
            if choice == 'b':
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(self.data_manager.routes):
                route = self.data_manager.routes[int(choice) - 1]
                self._display_route_details(route)
                
    def _display_route_details(self, route):
        """Display detailed information for a specific route."""
        clear_screen()
        print(center_text(f"=== Details for Route {route['route_id']} ===\n"))
        print(center_text(f"Timestamp: {route['timestamp']}"))
        print(center_text(f"Total Distance: {route['total_distance']:.1f} km"))
        print(center_text(f"Collection Amount: {route['collection_amount']:.1f} tons"))
        print(center_text(f"Priority Score: {route['priority_score']:.2f}"))
        print(center_text(f"\nBins Served: {len(route['bins_served'])}"))
        
        # Display bin details
        print(center_text("\nBin Details:"))
        for bin_id in route['bins_served']:
            bin_data = self.data_manager.get_bin(bin_id)
            if bin_data:
                print(center_text(
                    f"Bin {bin_id}: Fill Level {bin_data.fill_level:.1f}%, "
                    f"Last Collection: {bin_data.last_collection}"
                ))
                
        input(center_text("\nPress Enter to continue..."))

    def _handle_simulation(self):
        if not self.route_planner or not self.route_planner.has_routes():
            print(center_text("No routes to simulate. Please plan routes first."))
            time.sleep(1.5)
            return
            
        clear_screen()
        print(center_text("=== Real-time Simulation ==="))
        print("\n")
        
        options = [
            "1. Generate Random Updates",
            "2. Manual Bin Update",
            "3. View Current Status",
            "B. Back to Main Menu"
        ]
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        if choice == '1':
            self._simulate_random_updates()
        elif choice == '2':
            self._manual_bin_update()
        elif choice == '3':
            self._handle_system_status()
        else:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def _simulate_random_updates(self):
        clear_screen()
        print(center_text("=== Random Updates Simulation ==="))
        print("\n")
        
        try:
            num_updates = int(input(center_text("Enter number of updates to simulate (1-10): ")))
            if not 1 <= num_updates <= 10:
                raise ValueError
                
            updates = self.data_generator.generate_updates(self.city_graph, num_updates)
            
            print("\nApplying updates:")
            for bin_id, new_fill in updates:
                self.city_graph.update_bin_fill_level(bin_id, new_fill)
                print(f"Bin {bin_id}: Fill level updated to {new_fill:.1f}")
                time.sleep(0.5)
                
            print(center_text("\nUpdates applied successfully!"))
            print(center_text("Re-optimizing routes..."))
            time.sleep(1)
            
            # Re-plan routes with updated data
            self.route_planner.plan_routes(len(self.route_planner.routes))
            self._view_route_stats()
            
        except ValueError:
            print(center_text("Invalid input. Please enter a number between 1 and 10."))
            time.sleep(1.5)
            
    def _manual_bin_update(self):
        clear_screen()
        print(center_text("=== Manual Bin Update ==="))
        print("\n")
        
        try:
            bin_id = int(input("Enter bin ID to update: "))
            if bin_id not in self.city_graph.bins:
                raise ValueError("Invalid bin ID")
                
            bin_data = self.city_graph.bins[bin_id]
            print(f"\nCurrent fill level: {bin_data.current_fill:.1f}/{bin_data.capacity:.1f}")
            
            new_fill = float(input("Enter new fill level: "))
            if not 0 <= new_fill <= bin_data.capacity:
                raise ValueError("Invalid fill level")
                
            self.city_graph.update_bin_fill_level(bin_id, new_fill)
            print(center_text("\nBin updated successfully!"))
            print(center_text("Re-optimizing routes..."))
            time.sleep(1)
            
            # Re-plan routes with updated data
            self.route_planner.plan_routes(len(self.route_planner.routes))
            self._view_route_stats()
            
        except ValueError as e:
            print(center_text(str(e)))
            time.sleep(1.5)
            
    def _handle_settings(self):
        clear_screen()
        print(center_text("=== System Settings ==="))
        print("\n")
        
        options = [
            "1. Configure Truck Parameters",
            "2. Configure Clustering Parameters",
            "3. Reset to Default Settings",
            "B. Back to Main Menu"
        ]
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        if choice == '1':
            self._configure_route_params()
        elif choice == '2':
            self._configure_clustering_params()
        elif choice == '3':
            self._reset_settings()
        else:
            print(center_text("Invalid choice. Please try again."))
            time.sleep(1.5)
            
    def _configure_clustering_params(self):
        clear_screen()
        print(center_text("=== Configure Clustering Parameters ==="))
        print("\n")
        
        try:
            print(f"Current max cluster distance: {self.settings['max_cluster_distance']}")
            new_distance = float(input("Enter new max cluster distance (20-100): "))
            if 20 <= new_distance <= 100:
                self.settings['max_cluster_distance'] = new_distance
                print(center_text("\nParameters updated successfully!"))
            else:
                print(center_text("\nInvalid value. No changes made."))
                
        except ValueError:
            print(center_text("Invalid input. Please enter a valid number."))
            
        time.sleep(1.5)
        
    def _reset_settings(self):
        self.settings = {
            'truck_capacity': 1000.0,
            'max_cluster_distance': 50.0,
            'num_trucks': 1
        }
        print(center_text("\nSettings reset to default values."))
        time.sleep(1.5)
        
    def _handle_help(self):
        clear_screen()
        print(center_text("=== Help ==="))
        print("\n")
        help_text = [
            "Smart Trash Truck Routing System Help",
            "===================================",
            "",
            "1. Generate Sample Data: Create test data for the system",
            "2. Load Existing Data: Load previously saved data",
            "3. View System Status: See current bin locations and fill levels",
            "4. Plan Routes: Create and optimize collection routes",
            "5. View Routes: Display current planned routes",
            "6. Simulate Updates: Test real-time update functionality",
            "7. Settings: Configure system parameters",
            "",
            "Press 'Q' at any time to quit the program",
            "Press 'B' to go back to the previous menu"
        ]
        
        for line in help_text:
            print(center_text(line))
            
        input(center_text("\nPress Enter to continue..."))
        
    def _handle_visualizations(self):
        if not self.city_graph:
            print(center_text("No data to visualize. Please generate or load data first."))
            time.sleep(1.5)
            return
            
        clear_screen()
        print(center_text("=== Visualizations ==="))
        print("\n")
        
        options = [
            "1. View City Graph",
            "2. View Routes",
            "3. View Clusters",
            "4. View Performance Metrics",
            "5. Save All Visualizations",
            "B. Back to Main Menu"
        ]
        
        centered_options = create_centered_menu(options)
        for option in centered_options:
            print(option)
            
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'b':
            self.go_back()
            return
            
        try:
            if choice == '1':
                self.visualizer.plot_city_graph(self.city_graph, save=False)
            elif choice == '2':
                if not self.route_planner or not self.route_planner.has_routes():
                    raise ValueError("No routes planned yet.")
                self.visualizer.plot_routes(self.city_graph, self.route_planner.routes, save=False)
            elif choice == '3':
                clusters = self.city_graph.get_bin_clusters(self.settings['max_cluster_distance'])
                self.visualizer.plot_clusters(self.city_graph, clusters, save=False)
            elif choice == '4':
                if not self.route_planner or not self.route_planner.has_routes():
                    raise ValueError("No routes planned yet.")
                self.visualizer.plot_metrics(self.city_graph, self.route_planner.routes, save=False)
            elif choice == '5':
                self._save_all_visualizations()
            else:
                raise ValueError("Invalid choice.")
                
        except ValueError as e:
            print(center_text(str(e)))
            time.sleep(1.5)
            
    def _save_all_visualizations(self):
        """Save all available visualizations."""
        print(center_text("\nSaving visualizations..."))
        
        # Save city graph
        self.visualizer.plot_city_graph(self.city_graph)
        print(center_text("City graph saved."))
        
        # Save clusters
        clusters = self.city_graph.get_bin_clusters(self.settings['max_cluster_distance'])
        self.visualizer.plot_clusters(self.city_graph, clusters)
        print(center_text("Clusters visualization saved."))
        
        # Save routes and metrics if available
        if self.route_planner and self.route_planner.has_routes():
            self.visualizer.plot_routes(self.city_graph, self.route_planner.routes)
            print(center_text("Routes visualization saved."))
            
            self.visualizer.plot_metrics(self.city_graph, self.route_planner.routes)
            print(center_text("Performance metrics saved."))
            
        print(center_text("\nAll visualizations saved in 'visualizations' directory."))
        time.sleep(2)

    def save_routes(self):
        """Save current routes to file."""
        if not self.route_planner or not self.route_planner.has_routes():
            print(center_text("No routes to save. Please plan routes first."))
            time.sleep(1.5)
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            routes_data = []
            
            for route in self.route_planner.routes:
                route_data = {
                    'bins_served': list(route.bin_sequence),
                    'total_distance': route.total_distance,
                    'total_collection': route.total_collection
                }
                routes_data.append(route_data)
                
            # Save routes using data manager
            self.data_manager.save_routes(routes_data, timestamp)
            print(center_text("\nRoutes saved successfully!"))
            
        except Exception as e:
            print(center_text(f"\nError saving routes: {str(e)}"))
            
        time.sleep(1.5) 