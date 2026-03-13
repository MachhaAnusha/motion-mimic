"""
Filter 1: Neon Phantom
Human stick outline with neon bright colours and glowing effects
"""

import numpy as np
import cv2
import math
from typing import List, Dict, Tuple
from .base_filter import BaseFilter


class NeonPhantomFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Neon colors for different body segments
        self.segment_colors = {
            'head': (255, 100, 255),      # Magenta
            'torso': (0, 255, 255),        # Cyan
            'left_arm': (50, 255, 50),     # Lime green
            'right_arm': (255, 50, 150),  # Hot pink
            'left_leg': (100, 150, 255),  # Electric blue
            'right_leg': (255, 200, 50)    # Orange
        }
        
        # Pulse animation
        self.pulse_time = 0
        self.scanline_offset = 0
        
        # MediaPipe pose connections
        self.pose_connections = [
            # Face
            (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
            # Torso
            (11, 12), (11, 23), (12, 24), (23, 24),
            # Left arm
            (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
            # Right arm
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
            # Left leg
            (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
            # Right leg
            (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
        ]
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply neon phantom filter"""
        canvas = self.create_black_canvas()
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Update animation
        self.pulse_time += 0.1
        self.scanline_offset = (self.scanline_offset + 2) % 20
        
        # Calculate movement intensity
        movement_intensity = self._calculate_movement_intensity(velocities)
        
        # Draw skeleton connections
        self._draw_skeleton(canvas, landmarks, movement_intensity)
        
        # Draw joints
        self._draw_joints(canvas, landmarks, movement_intensity)
        
        # Add scanline overlay
        self._add_scanlines(canvas)
        
        return canvas
        
    def _calculate_movement_intensity(self, velocities: List[Dict]) -> float:
        """Calculate overall movement intensity"""
        if not velocities:
            return 0.5
            
        total_velocity = sum(v.get('magnitude', 0) for v in velocities)
        normalized = min(1.0, total_velocity / 100.0)
        return 0.3 + 0.7 * normalized  # Range from 0.3 to 1.0
        
    def _get_segment_color(self, connection: Tuple[int, int]) -> Tuple[int, int, int]:
        """Get color for a body segment based on connection"""
        # Map connections to body segments
        if connection[0] in [0, 1, 2, 3, 4, 5, 6, 7, 8]:  # Face/head
            return self.segment_colors['head']
        elif connection[0] in [11, 12, 23, 24]:  # Torso
            return self.segment_colors['torso']
        elif connection[0] in [11, 13, 15, 17, 19, 21]:  # Left arm
            return self.segment_colors['left_arm']
        elif connection[0] in [12, 14, 16, 18, 20, 22]:  # Right arm
            return self.segment_colors['right_arm']
        elif connection[0] in [23, 25, 27, 29, 31]:  # Left leg
            return self.segment_colors['left_leg']
        elif connection[0] in [24, 26, 28, 30, 32]:  # Right leg
            return self.segment_colors['right_leg']
        else:
            return (255, 255, 255)  # Default white
            
    def _draw_skeleton(self, canvas: np.ndarray, landmarks: List[Dict], 
                      movement_intensity: float):
        """Draw skeleton connections with neon glow"""
        for connection in self.pose_connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                # Convert to pixel coordinates
                x1, y1 = int(pt1['x'] * self.width), int(pt1['y'] * self.height)
                x2, y2 = int(pt2['x'] * self.width), int(pt2['y'] * self.height)
                
                # Get segment color
                color = self._get_segment_color(connection)
                
                # Draw glowing line with intensity based on movement
                glow_intensity = movement_intensity * self.intensity
                thickness = int(3 + 2 * movement_intensity)
                self.draw_glowing_line(canvas, (x1, y1), (x2, y2), color, thickness, glow_intensity)
                
    def _draw_joints(self, canvas: np.ndarray, landmarks: List[Dict], 
                    movement_intensity: float):
        """Draw joints with pulsing glow effect"""
        for i, landmark in enumerate(landmarks):
            if landmark['visibility'] > 0.5:  # Only draw visible joints
                x, y = int(landmark['x'] * self.width), int(landmark['y'] * self.height)
                
                # Pulsing effect
                pulse = 1.0 + 0.3 * math.sin(self.pulse_time + i * 0.2)
                
                # Joint color based on position
                if i < 11:  # Face/head
                    color = self.segment_colors['head']
                elif i < 23:  # Arms
                    color = self.segment_colors['left_arm'] if i % 2 == 1 else self.segment_colors['right_arm']
                else:  # Legs
                    color = self.segment_colors['left_leg'] if i % 2 == 1 else self.segment_colors['right_leg']
                    
                # Draw glowing joint
                radius = int(5 + 3 * movement_intensity)
                self.draw_glowing_circle(canvas, (x, y), radius, color, pulse)
                
    def _add_scanlines(self, canvas: np.ndarray):
        """Add retro scanline overlay"""
        for y in range(0, self.height, 4):
            alpha = 30 if (y + self.scanline_offset) % 20 < 10 else 10
            cv2.line(canvas, (0, y), (self.width, y), (0, 255, 255), 1)
            
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw message when no person is detected"""
        text = "Step into frame"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        # Glowing text effect
        for i in range(3):
            color = (100 - i*20, 255 - i*50, 255 - i*50)
            cv2.putText(canvas, text, (text_x, text_y), font, 1.0, color, 3-i)
            
    def reset(self):
        """Reset filter state"""
        self.pulse_time = 0
        self.scanline_offset = 0
