import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import networkx as nx
from dataclasses import dataclass, asdict
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class BinRecord:
    bin_id: str
    location: tuple
    fill_level: float
    last_collection: str
    collection_history: List[Dict]

@dataclass_json
@dataclass
class RouteRecord:
    route_id: str
    timestamp: str
    bins_served: List[str]
    total_distance: float
    priority_score: float
    collection_amount: float

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.bins_file = os.path.join(data_dir, "bins.json")
        self.routes_file = os.path.join(data_dir, "routes.json")
        self.records_file = os.path.join(data_dir, "collection_records.json")
        self._ensure_data_directory()
        self._load_data()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_data(self):
        """Load existing data from files."""
        self.bins = self._load_json(self.bins_file, {})
        self.routes = self._load_json(self.routes_file, [])
        self.records = self._load_json(self.records_file, {
            "collection_history": [],
            "system_stats": {
                "total_collections": 0,
                "total_distance": 0,
                "total_waste_collected": 0
            }
        })

    def _load_json(self, file_path: str, default_value: any) -> any:
        """Load JSON data from file with error handling."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Error reading {file_path}, using default value")
        return default_value

    def _save_json(self, data: any, file_path: str):
        """Save data to JSON file with error handling."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data to {file_path}: {str(e)}")

    def update_bin(self, bin_record: BinRecord):
        """Update or add a bin record."""
        self.bins[bin_record.bin_id] = asdict(bin_record)
        self._save_json(self.bins, self.bins_file)

    def get_bin(self, bin_id: str) -> Optional[BinRecord]:
        """Retrieve a bin record."""
        if bin_id in self.bins:
            return BinRecord.from_dict(self.bins[bin_id])
        return None

    def add_route_record(self, route: RouteRecord):
        """Add a new route record."""
        self.routes.append(asdict(route))
        self._save_json(self.routes, self.routes_file)
        
        # Update system stats
        self.records["system_stats"]["total_collections"] += 1
        self.records["system_stats"]["total_distance"] += route.total_distance
        self.records["system_stats"]["total_waste_collected"] += route.collection_amount
        
        # Add to collection history
        self.records["collection_history"].append({
            "timestamp": route.timestamp,
            "route_id": route.route_id,
            "bins_served": route.bins_served,
            "collection_amount": route.collection_amount
        })
        
        self._save_json(self.records, self.records_file)

    def save_routes(self, routes_data: List[Dict], timestamp: str = None):
        """Save routes data with timestamp."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        route_records = []
        for i, route in enumerate(routes_data):
            route_record = RouteRecord(
                route_id=f"route_{timestamp}_{i+1}",
                timestamp=timestamp,
                bins_served=route['bins_served'],
                total_distance=route['total_distance'],
                priority_score=sum(self.get_bin(bin_id).fill_level 
                                 for bin_id in route['bins_served']),
                collection_amount=route['total_collection']
            )
            route_records.append(asdict(route_record))
            
        # Add to routes list
        self.routes.extend(route_records)
        self._save_json(self.routes, self.routes_file)
        
        # Update system stats
        total_distance = sum(r['total_distance'] for r in route_records)
        total_collection = sum(r['collection_amount'] for r in route_records)
        
        self.records["system_stats"]["total_collections"] += len(route_records)
        self.records["system_stats"]["total_distance"] += total_distance
        self.records["system_stats"]["total_waste_collected"] += total_collection
        
        # Add to collection history
        for record in route_records:
            self.records["collection_history"].append({
                "timestamp": record['timestamp'],
                "route_id": record['route_id'],
                "bins_served": record['bins_served'],
                "collection_amount": record['collection_amount']
            })
            
        self._save_json(self.records, self.records_file)

    def get_system_stats(self) -> Dict:
        """Get system-wide statistics."""
        return self.records["system_stats"]

    def get_bin_collection_history(self, bin_id: str) -> List[Dict]:
        """Get collection history for a specific bin."""
        bin_record = self.get_bin(bin_id)
        return bin_record.collection_history if bin_record else []

    def export_data(self, export_dir: str = "exports"):
        """Export all data to a timestamped directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(export_dir, f"data_export_{timestamp}")
        os.makedirs(export_path, exist_ok=True)
        
        # Export each data file
        self._save_json(self.bins, os.path.join(export_path, "bins_export.json"))
        self._save_json(self.routes, os.path.join(export_path, "routes_export.json"))
        self._save_json(self.records, os.path.join(export_path, "records_export.json"))
        
        # Create a summary file
        summary = {
            "export_time": timestamp,
            "total_bins": len(self.bins),
            "total_routes": len(self.routes),
            "system_stats": self.records["system_stats"]
        }
        self._save_json(summary, os.path.join(export_path, "export_summary.json"))
        
        return export_path

    def import_data(self, import_dir: str):
        """Import data from a previous export."""
        try:
            # Import each data file
            bins_file = os.path.join(import_dir, "bins_export.json")
            routes_file = os.path.join(import_dir, "routes_export.json")
            records_file = os.path.join(import_dir, "records_export.json")
            
            if os.path.exists(bins_file):
                self.bins = self._load_json(bins_file, self.bins)
            if os.path.exists(routes_file):
                self.routes = self._load_json(routes_file, self.routes)
            if os.path.exists(records_file):
                self.records = self._load_json(records_file, self.records)
                
            # Save imported data to current files
            self._save_json(self.bins, self.bins_file)
            self._save_json(self.routes, self.routes_file)
            self._save_json(self.records, self.records_file)
            
            return True
        except Exception as e:
            print(f"Error importing data: {str(e)}")
            return False

    def clear_data(self):
        """Clear all data (with confirmation required)."""
        self.bins = {}
        self.routes = []
        self.records = {
            "collection_history": [],
            "system_stats": {
                "total_collections": 0,
                "total_distance": 0,
                "total_waste_collected": 0
            }
        }
        
        self._save_json(self.bins, self.bins_file)
        self._save_json(self.routes, self.routes_file)
        self._save_json(self.records, self.records_file) 