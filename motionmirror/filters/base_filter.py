"""
Base filter class for all visual effects
"""

import numpy as np
import cv2
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class BaseFilter(ABC):
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.intensity = 1.0
        self.enabled = True
        
    @abstractmethod
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply filter to frame with pose data"""
        pass
        
    def create_black_canvas(self) -> np.ndarray:
        """Create a pure black canvas"""
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
    def draw_glowing_line(self, canvas: np.ndarray, pt1: Tuple[int, int], 
                         pt2: Tuple[int, int], color: Tuple[int, int, int], 
                         thickness: int = 3, glow_intensity: float = 1.0):
        """Draw a line with glowing effect"""
        # Draw multiple layers for glow effect
        glow_colors = [
            (color[0]//4, color[1]//4, color[2]//4),  # Dark outer glow
            (color[0]//2, color[1]//2, color[2]//2),  # Medium glow
            color,  # Main color
            (255, 255, 255)  # White center
        ]
        
        glow_thicknesses = [thickness * 3, thickness * 2, thickness, max(1, thickness//2)]
        
        for i, (gcolor, gthickness) in enumerate(zip(glow_colors, glow_thicknesses)):
            alpha = glow_intensity * (0.3 if i < 2 else 0.8)
            cv2.line(canvas, pt1, pt2, gcolor, gthickness)
            
    def draw_glowing_circle(self, canvas: np.ndarray, center: Tuple[int, int], 
                           radius: int, color: Tuple[int, int, int], 
                           pulse: float = 1.0):
        """Draw a circle with glowing effect"""
        # Pulsing radius
        pulse_radius = int(radius * pulse)
        
        # Draw glow layers
        for i in range(3):
            glow_radius = pulse_radius + (3-i) * 3
            glow_color = tuple(c // (i+1) for c in color)
            cv2.circle(canvas, center, glow_radius, glow_color, -1)
            
        # Draw main circle
        cv2.circle(canvas, center, pulse_radius, color, -1)
        
        # White center
        cv2.circle(canvas, center, max(1, pulse_radius//2), (255, 255, 255), -1)
        
    def set_intensity(self, intensity: float):
        """Set filter intensity (0.0 to 1.0)"""
        self.intensity = max(0.0, min(1.0, intensity))
        
    def set_enabled(self, enabled: bool):
        """Enable or disable filter"""
        self.enabled = enabled
        
    def reset(self):
        """Reset filter state"""
        pass
