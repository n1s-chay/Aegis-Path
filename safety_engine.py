"""
Safety Engine Module
Combines camera analysis and incident reports to calculate safety scores
"""
from typing import Dict, List, Tuple
import logging
from camera_analyzer import CameraAnalyzer
from incident_manager import IncidentManager
from config import Config

logger = logging.getLogger(__name__)


class SafetyEngine:
    """Engine for calculating safety scores for locations"""
    
    def __init__(self, config: Config = None):
        """
        Initialize the safety engine
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.camera_analyzer = CameraAnalyzer()
        self.incident_manager = IncidentManager()
    
    def calculate_location_safety(self, location: Tuple[float, float],
                                  camera_data: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calculate comprehensive safety score for a location
        
        Args:
            location: (latitude, longitude) tuple
            camera_data: Optional pre-analyzed camera data
            
        Returns:
            Dictionary with safety metrics
        """
        # Get incident-based safety score
        incident_score = self.incident_manager.calculate_safety_score(location)
        
        # Get camera analysis if not provided
        if camera_data is None:
            camera_data = {'lighting': 50.0, 'crowd_density': 50.0}
        
        lighting_score = camera_data.get('lighting', 50.0)
        crowd_density = camera_data.get('crowd_density', 50.0)
        
        # Convert crowd density to safety score (lower density = safer)
        crowd_safety_score = 100 - crowd_density
        
        # Calculate weighted overall safety score
        overall_safety = (
            incident_score * self.config.INCIDENT_WEIGHT +
            lighting_score * self.config.LIGHTING_WEIGHT +
            crowd_safety_score * self.config.CROWD_WEIGHT
        )
        
        return {
            'overall_safety': float(overall_safety),
            'incident_score': float(incident_score),
            'lighting_score': float(lighting_score),
            'crowd_density': float(crowd_density),
            'crowd_safety_score': float(crowd_safety_score)
        }
    
    def evaluate_path_segment(self, start: Tuple[float, float], 
                             end: Tuple[float, float]) -> float:
        """
        Evaluate safety of a path segment
        
        Args:
            start: Starting coordinate (lat, lng)
            end: Ending coordinate (lat, lng)
            
        Returns:
            Safety score for the segment (0-100)
        """
        # Calculate midpoint
        mid_lat = (start[0] + end[0]) / 2
        mid_lng = (start[1] + end[1]) / 2
        midpoint = (mid_lat, mid_lng)
        
        # Evaluate safety at start, middle, and end
        start_safety = self.calculate_location_safety(start)
        mid_safety = self.calculate_location_safety(midpoint)
        end_safety = self.calculate_location_safety(end)
        
        # Use minimum safety as segment safety (conservative approach)
        segment_safety = min(
            start_safety['overall_safety'],
            mid_safety['overall_safety'],
            end_safety['overall_safety']
        )
        
        return float(segment_safety)
    
    def evaluate_path(self, waypoints: List[Tuple[float, float]]) -> Dict[str, any]:
        """
        Evaluate safety of an entire path
        
        Args:
            waypoints: List of coordinates along the path
            
        Returns:
            Dictionary with path safety metrics
        """
        if len(waypoints) < 2:
            return {
                'overall_safety': 0.0,
                'segments': [],
                'is_safe': False
            }
        
        segment_scores = []
        
        # Evaluate each segment
        for i in range(len(waypoints) - 1):
            segment_safety = self.evaluate_path_segment(waypoints[i], waypoints[i + 1])
            segment_scores.append({
                'start': waypoints[i],
                'end': waypoints[i + 1],
                'safety': segment_safety
            })
        
        # Calculate overall path safety (average of segments)
        overall_safety = sum(s['safety'] for s in segment_scores) / len(segment_scores)
        
        # Determine if path is safe enough
        is_safe = overall_safety >= self.config.SAFETY_THRESHOLD
        
        return {
            'overall_safety': float(overall_safety),
            'segments': segment_scores,
            'is_safe': is_safe,
            'min_segment_safety': float(min(s['safety'] for s in segment_scores)),
            'max_segment_safety': float(max(s['safety'] for s in segment_scores))
        }
