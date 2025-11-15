"""
Path Finding Module
Calculates safe routes between two points
"""
from typing import List, Tuple, Dict
import logging
from safety_engine import SafetyEngine
from config import Config

logger = logging.getLogger(__name__)


class PathNode:
    """Represents a node in the path network"""
    
    def __init__(self, location: Tuple[float, float]):
        self.location = location
        self.safety_score = 0.0
        self.distance = float('inf')
        self.previous = None
    
    def __lt__(self, other):
        # For priority queue comparisons
        return self.distance < other.distance


class PathFinder:
    """Finds safe paths between two points"""
    
    def __init__(self, config: Config = None):
        """
        Initialize the path finder
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.safety_engine = SafetyEngine(config)
    
    def find_safe_path(self, start: Tuple[float, float], 
                       end: Tuple[float, float]) -> Dict[str, any]:
        """
        Find the safest path between two points
        
        Args:
            start: Starting coordinate (lat, lng)
            end: Ending coordinate (lat, lng)
            
        Returns:
            Dictionary with path information
        """
        # For now, generate a simple direct path with waypoints
        # In a production system, this would use actual road network data
        waypoints = self._generate_direct_path(start, end)
        
        # Evaluate the path
        path_evaluation = self.safety_engine.evaluate_path(waypoints)
        
        return {
            'waypoints': waypoints,
            'safety_score': path_evaluation['overall_safety'],
            'is_safe': path_evaluation['is_safe'],
            'segments': path_evaluation['segments'],
            'distance_km': self._calculate_path_distance(waypoints)
        }
    
    def find_alternative_paths(self, start: Tuple[float, float],
                              end: Tuple[float, float],
                              num_alternatives: int = None) -> List[Dict[str, any]]:
        """
        Find multiple alternative paths
        
        Args:
            start: Starting coordinate (lat, lng)
            end: Ending coordinate (lat, lng)
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of path dictionaries
        """
        if num_alternatives is None:
            num_alternatives = self.config.MAX_ALTERNATIVE_PATHS
        
        paths = []
        
        # Main direct path
        main_path = self.find_safe_path(start, end)
        paths.append(main_path)
        
        # Generate alternative paths with slight variations
        for i in range(num_alternatives - 1):
            alt_waypoints = self._generate_alternative_path(start, end, variation=i+1)
            alt_evaluation = self.safety_engine.evaluate_path(alt_waypoints)
            
            paths.append({
                'waypoints': alt_waypoints,
                'safety_score': alt_evaluation['overall_safety'],
                'is_safe': alt_evaluation['is_safe'],
                'segments': alt_evaluation['segments'],
                'distance_km': self._calculate_path_distance(alt_waypoints)
            })
        
        # Sort by safety score (highest first)
        paths.sort(key=lambda p: p['safety_score'], reverse=True)
        
        return paths
    
    def _generate_direct_path(self, start: Tuple[float, float],
                             end: Tuple[float, float],
                             num_waypoints: int = 5) -> List[Tuple[float, float]]:
        """
        Generate a direct path with intermediate waypoints
        
        Args:
            start: Starting coordinate
            end: Ending coordinate
            num_waypoints: Total number of waypoints including start and end
            
        Returns:
            List of waypoints
        """
        waypoints = [start]
        
        # Generate intermediate waypoints
        for i in range(1, num_waypoints - 1):
            factor = i / (num_waypoints - 1)
            lat = start[0] + (end[0] - start[0]) * factor
            lng = start[1] + (end[1] - start[1]) * factor
            waypoints.append((lat, lng))
        
        waypoints.append(end)
        return waypoints
    
    def _generate_alternative_path(self, start: Tuple[float, float],
                                  end: Tuple[float, float],
                                  variation: int = 1) -> List[Tuple[float, float]]:
        """
        Generate an alternative path with offset
        
        Args:
            start: Starting coordinate
            end: Ending coordinate
            variation: Variation number (affects offset direction)
            
        Returns:
            List of waypoints for alternative path
        """
        waypoints = [start]
        num_waypoints = 5
        
        # Calculate perpendicular offset
        offset_factor = 0.002 * variation  # Small offset in degrees
        
        for i in range(1, num_waypoints - 1):
            factor = i / (num_waypoints - 1)
            lat = start[0] + (end[0] - start[0]) * factor
            lng = start[1] + (end[1] - start[1]) * factor
            
            # Add perpendicular offset
            if variation % 2 == 0:
                lat += offset_factor
            else:
                lng += offset_factor
            
            waypoints.append((lat, lng))
        
        waypoints.append(end)
        return waypoints
    
    def _calculate_path_distance(self, waypoints: List[Tuple[float, float]]) -> float:
        """
        Calculate total distance of a path
        
        Args:
            waypoints: List of coordinates
            
        Returns:
            Distance in kilometers
        """
        total_distance = 0.0
        
        for i in range(len(waypoints) - 1):
            distance = self._calculate_distance(waypoints[i], waypoints[i + 1])
            total_distance += distance
        
        return total_distance
    
    def _calculate_distance(self, loc1: Tuple[float, float],
                          loc2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates
        
        Args:
            loc1: First coordinate (lat, lng)
            loc2: Second coordinate (lat, lng)
            
        Returns:
            Distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        r = 6371  # Radius of earth in kilometers
        
        return c * r
