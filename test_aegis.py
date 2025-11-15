"""
Test script for Aegis-Path application
Demonstrates core functionality
"""
import sys
from pathfinder import PathFinder
from camera_analyzer import CameraAnalyzer
from incident_manager import IncidentManager, IncidentReport
from safety_engine import SafetyEngine
from datetime import datetime


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_incident_manager():
    """Test incident management"""
    print_section("Testing Incident Manager")
    
    manager = IncidentManager()
    
    # Add a test incident
    test_incident = IncidentReport(
        incident_id="TEST-001",
        location=(12.9716, 77.5946),
        incident_type="test",
        severity=2,
        timestamp=datetime.now()
    )
    
    print(f"Total incidents loaded: {len(manager.incidents)}")
    
    # Get incidents near a location
    location = (12.9716, 77.5946)
    nearby = manager.get_incidents_near_location(location, radius_km=2.0)
    print(f"Incidents within 2km of ({location[0]}, {location[1]}): {len(nearby)}")
    
    # Calculate safety score
    safety = manager.calculate_safety_score(location)
    print(f"Safety score for location: {safety:.2f}/100")


def test_camera_analyzer():
    """Test camera analysis"""
    print_section("Testing Camera Analyzer")
    
    analyzer = CameraAnalyzer()
    
    # Test with a synthetic frame (would normally be from camera)
    import numpy as np
    
    # Create a test image (bright, moderate contrast)
    test_frame = np.random.randint(100, 200, (480, 640, 3), dtype=np.uint8)
    
    analysis = analyzer.analyze_frame(test_frame)
    print(f"Lighting score: {analysis['lighting']:.2f}/100")
    print(f"Crowd density: {analysis['crowd_density']:.2f}/100")


def test_safety_engine():
    """Test safety engine"""
    print_section("Testing Safety Engine")
    
    engine = SafetyEngine()
    
    location = (12.9716, 77.5946)
    safety_data = engine.calculate_location_safety(location)
    
    print(f"Overall safety: {safety_data['overall_safety']:.2f}/100")
    print(f"Incident score: {safety_data['incident_score']:.2f}/100")
    print(f"Lighting score: {safety_data['lighting_score']:.2f}/100")
    print(f"Crowd density: {safety_data['crowd_density']:.2f}/100")


def test_pathfinder():
    """Test pathfinding"""
    print_section("Testing Path Finder")
    
    finder = PathFinder()
    
    # Test path from Bangalore location to another
    start = (12.9716, 77.5946)  # Example: Near MG Road
    end = (12.9352, 77.6245)    # Example: Near Koramangala
    
    print(f"Finding path from {start} to {end}")
    
    # Find single safe path
    path = finder.find_safe_path(start, end)
    print(f"\nSafest Path:")
    print(f"  Safety Score: {path['safety_score']:.2f}/100")
    print(f"  Distance: {path['distance_km']:.2f} km")
    print(f"  Is Safe: {'Yes' if path['is_safe'] else 'No (use caution)'}")
    print(f"  Waypoints: {len(path['waypoints'])}")
    
    # Find alternative paths
    print("\nFinding alternative paths...")
    alt_paths = finder.find_alternative_paths(start, end, num_alternatives=3)
    
    for i, alt_path in enumerate(alt_paths, 1):
        print(f"\nPath {i}:")
        print(f"  Safety Score: {alt_path['safety_score']:.2f}/100")
        print(f"  Distance: {alt_path['distance_km']:.2f} km")
        print(f"  Is Safe: {'Yes' if alt_path['is_safe'] else 'No (use caution)'}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  AEGIS-PATH TEST SUITE")
    print("  Women Safety App - Smart Surveillance")
    print("=" * 60)
    
    try:
        test_incident_manager()
        test_camera_analyzer()
        test_safety_engine()
        test_pathfinder()
        
        print_section("All Tests Completed Successfully!")
        print("\nYou can now:")
        print("1. Start the API server: python app.py")
        print("2. Open index.html in your browser")
        print("3. Use the API endpoints for integration")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
