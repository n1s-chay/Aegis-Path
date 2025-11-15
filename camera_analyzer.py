"""
Camera Analysis Module
Uses OpenCV to analyze camera feeds for lighting conditions and crowd density
"""
import cv2
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CameraAnalyzer:
    """Analyzes camera feeds for safety metrics"""
    
    def __init__(self):
        """Initialize the camera analyzer"""
        self.face_cascade = None
        try:
            # Load pre-trained cascade for people detection (using face detection as proxy)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            logger.warning(f"Could not load face cascade: {e}")
    
    def analyze_lighting(self, frame: np.ndarray) -> float:
        """
        Analyze lighting conditions in a frame
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            Lighting score (0-100, higher is better lit)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate mean brightness
            mean_brightness = np.mean(gray)
            
            # Calculate contrast (standard deviation)
            contrast = np.std(gray)
            
            # Lighting score based on brightness and contrast
            # Good lighting: bright enough (120-200) with good contrast (>30)
            brightness_score = min(100, (mean_brightness / 200) * 100)
            contrast_score = min(100, (contrast / 50) * 100)
            
            # Weighted combination
            lighting_score = (brightness_score * 0.7) + (contrast_score * 0.3)
            
            return float(lighting_score)
        except Exception as e:
            logger.error(f"Error analyzing lighting: {e}")
            return 50.0  # Default moderate score
    
    def analyze_crowd_density(self, frame: np.ndarray) -> float:
        """
        Analyze crowd density in a frame
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            Crowd density score (0-100, higher means more crowded)
        """
        try:
            if self.face_cascade is None:
                return 50.0  # Default moderate density
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces as proxy for people
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Calculate density based on number of people and frame size
            frame_area = frame.shape[0] * frame.shape[1]
            people_count = len(faces)
            
            # Normalize to 0-100 scale
            # Assume 20+ people in frame is very crowded
            density_score = min(100, (people_count / 20) * 100)
            
            return float(density_score)
        except Exception as e:
            logger.error(f"Error analyzing crowd density: {e}")
            return 50.0  # Default moderate density
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Perform complete analysis of a frame
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            Dictionary with lighting and crowd density scores
        """
        return {
            'lighting': self.analyze_lighting(frame),
            'crowd_density': self.analyze_crowd_density(frame)
        }
    
    def analyze_camera_feed(self, camera_url: str) -> Dict[str, float]:
        """
        Analyze a camera feed URL
        
        Args:
            camera_url: URL or path to camera feed
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Open camera feed
            cap = cv2.VideoCapture(camera_url)
            
            if not cap.isOpened():
                logger.error(f"Could not open camera feed: {camera_url}")
                return {'lighting': 50.0, 'crowd_density': 50.0}
            
            # Read a frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.error(f"Could not read frame from camera: {camera_url}")
                return {'lighting': 50.0, 'crowd_density': 50.0}
            
            return self.analyze_frame(frame)
        except Exception as e:
            logger.error(f"Error analyzing camera feed {camera_url}: {e}")
            return {'lighting': 50.0, 'crowd_density': 50.0}
    
    def analyze_image_file(self, image_path: str) -> Dict[str, float]:
        """
        Analyze a static image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"Could not read image: {image_path}")
                return {'lighting': 50.0, 'crowd_density': 50.0}
            
            return self.analyze_frame(frame)
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {'lighting': 50.0, 'crowd_density': 50.0}
