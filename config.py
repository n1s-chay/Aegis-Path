"""
Configuration file for Aegis-Path application
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Camera configuration
    CAMERA_FEED_URLS = os.environ.get('CAMERA_FEED_URLS', '').split(',')
    
    # Safety thresholds
    MIN_LIGHTING_SCORE = 40  # 0-100 scale
    MAX_CROWD_DENSITY = 80   # 0-100 scale (higher = more crowded)
    INCIDENT_WEIGHT = 0.3    # Weight for police incidents in safety score
    LIGHTING_WEIGHT = 0.4    # Weight for lighting in safety score
    CROWD_WEIGHT = 0.3       # Weight for crowd density in safety score
    
    # Pathfinding
    MAX_ALTERNATIVE_PATHS = 3
    SAFETY_THRESHOLD = 60    # Minimum safety score (0-100) for a path
    
    # API configuration
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'aegis_path.db'
