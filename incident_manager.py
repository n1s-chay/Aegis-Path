"""
Incident Reports Module
Manages police incident reports and their impact on path safety
"""
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IncidentReport:
    """Represents a police incident report"""
    
    def __init__(self, incident_id: str, location: Tuple[float, float], 
                 incident_type: str, severity: int, timestamp: datetime):
        """
        Initialize an incident report
        
        Args:
            incident_id: Unique identifier for the incident
            location: (latitude, longitude) tuple
            incident_type: Type of incident (e.g., 'theft', 'assault', 'harassment')
            severity: Severity level (1-5, 5 being most severe)
            timestamp: When the incident occurred
        """
        self.incident_id = incident_id
        self.location = location
        self.incident_type = incident_type
        self.severity = severity
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'incident_id': self.incident_id,
            'location': {'lat': self.location[0], 'lng': self.location[1]},
            'incident_type': self.incident_type,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IncidentReport':
        """Create from dictionary"""
        return cls(
            incident_id=data['incident_id'],
            location=(data['location']['lat'], data['location']['lng']),
            incident_type=data['incident_type'],
            severity=data['severity'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class IncidentManager:
    """Manages incident reports and queries"""
    
    def __init__(self, data_file: str = 'incidents.json'):
        """
        Initialize the incident manager
        
        Args:
            data_file: Path to JSON file storing incidents
        """
        self.data_file = data_file
        self.incidents: List[IncidentReport] = []
        self.load_incidents()
    
    def load_incidents(self):
        """Load incidents from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.incidents = [IncidentReport.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.incidents)} incidents")
            except Exception as e:
                logger.error(f"Error loading incidents: {e}")
                self.incidents = []
        else:
            logger.info("No incident file found, starting with empty database")
            self.incidents = []
    
    def save_incidents(self):
        """Save incidents to file"""
        try:
            with open(self.data_file, 'w') as f:
                data = [incident.to_dict() for incident in self.incidents]
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.incidents)} incidents")
        except Exception as e:
            logger.error(f"Error saving incidents: {e}")
    
    def add_incident(self, incident: IncidentReport):
        """Add a new incident"""
        self.incidents.append(incident)
        self.save_incidents()
    
    def get_incidents_near_location(self, location: Tuple[float, float], 
                                   radius_km: float = 1.0,
                                   days_back: int = 365) -> List[IncidentReport]:
        """
        Get incidents near a location within a time window
        
        Args:
            location: (latitude, longitude) tuple
            radius_km: Search radius in kilometers
            days_back: How many days back to search
            
        Returns:
            List of relevant incidents
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_incidents = []
        
        for incident in self.incidents:
            # Check if incident is recent enough
            if incident.timestamp < cutoff_date:
                continue
            
            # Calculate distance (simplified Haversine)
            distance = self._calculate_distance(location, incident.location)
            
            if distance <= radius_km:
                relevant_incidents.append(incident)
        
        return relevant_incidents
    
    def _calculate_distance(self, loc1: Tuple[float, float], 
                          loc2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates in kilometers
        
        Args:
            loc1: (latitude, longitude) tuple
            loc2: (latitude, longitude) tuple
            
        Returns:
            Distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Convert to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def calculate_safety_score(self, location: Tuple[float, float],
                              radius_km: float = 0.5) -> float:
        """
        Calculate safety score for a location based on incidents
        
        Args:
            location: (latitude, longitude) tuple
            radius_km: Search radius in kilometers
            
        Returns:
            Safety score (0-100, higher is safer)
        """
        incidents = self.get_incidents_near_location(location, radius_km)
        
        if not incidents:
            return 100.0  # No incidents = very safe
        
        # Calculate weighted severity
        total_weight = 0
        for incident in incidents:
            # More recent incidents have higher weight
            days_ago = (datetime.now() - incident.timestamp).days
            recency_factor = max(0.1, 1.0 - (days_ago / 365))
            
            # Higher severity has higher weight
            severity_factor = incident.severity / 5.0
            
            total_weight += recency_factor * severity_factor
        
        # Convert to 0-100 scale (more incidents = lower score)
        # Assume 5+ weighted incidents makes area very unsafe
        safety_score = max(0, 100 - (total_weight / 5.0) * 100)
        
        return float(safety_score)
