"""
Filter 5: Silk Trails
3D ribbon / smoke trails from joints with smooth bezier curves
"""

import numpy as np
import cv2
import math
from typing import List, Dict, Tuple
from collections import deque
from .base_filter import BaseFilter


class SilkTrailsFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Major joints to track
        self.joint_indices = {
            'left_wrist': 15,
            'right_wrist': 16,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
            'left_hip': 23,
            'right_hip': 24
        }
        
        # Ribbon colors for each joint
        self.ribbon_colors = {
            'left_wrist': (255, 100, 100),    # Red
            'right_wrist': (100, 255, 100),  # Green
            'left_elbow': (100, 100, 255),   # Blue
            'right_elbow': (255, 255, 100),  # Yellow
            'left_shoulder': (255, 100, 255), # Magenta
            'right_shoulder': (100, 255, 255), # Cyan
            'left_knee': (255, 165, 0),      # Orange
            'right_knee': (255, 192, 203),   # Pink
            'left_ankle': (148, 0, 211),     # Violet
            'right_ankle': (0, 255, 127),    # Spring green
            'left_hip': (64, 224, 208),      # Turquoise
            'right_hip': (255, 215, 0)       # Gold
        }
        
        # Trail storage for each joint
        self.trail_length = 40
        self.joint_trails = {joint_name: deque(maxlen=self.trail_length) 
                           for joint_name in self.joint_indices.keys()}
        
        # Animation parameters
        self.turbulence_time = 0
        self.turbulence_frequency = 0.1
        self.turbulence_amplitude = 5.0
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply silk trails filter"""
        canvas = self.create_black_canvas()
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Update animation
        self.turbulence_time += self.turbulence_frequency
        
        # Update joint trails
        self._update_trails(landmarks, velocities)
        
        # Draw ribbon trails
        self._draw_ribbon_trails(canvas)
        
        # Draw current joints as glowing points
        self._draw_current_joints(canvas, landmarks)
        
        return canvas
        
    def _update_trails(self, landmarks: List[Dict], velocities: List[Dict]):
        """Update trail positions for all joints"""
        for joint_name, landmark_idx in self.joint_indices.items():
            if landmark_idx < len(landmarks):
                landmark = landmarks[landmark_idx]
                
                # Get current position
                x = landmark['x'] * self.width
                y = landmark['y'] * self.height
                
                # Get velocity for this joint
                velocity = 0
                if landmark_idx < len(velocities):
                    velocity = velocities[landmark_idx].get('magnitude', 0)
                
                # Store position with velocity
                self.joint_trails[joint_name].append({
                    'x': x,
                    'y': y,
                    'velocity': velocity,
                    'timestamp': len(self.joint_trails[joint_name])
                })
                
    def _draw_ribbon_trails(self, canvas: np.ndarray):
        """Draw smooth ribbon trails for all joints"""
        for joint_name, trail in self.joint_trails.items():
            if len(trail) < 2:
                continue
                
            color = self.ribbon_colors[joint_name]
            self._draw_single_ribbon(canvas, trail, color)
            
    def _draw_single_ribbon(self, canvas: np.ndarray, trail: List[Dict], 
                           color: Tuple[int, int, int]):
        """Draw a single ribbon trail with bezier curves"""
        if len(trail) < 2:
            return
            
        # Convert trail to points
        points = [(int(p['x']), int(p['y'])) for p in trail]
        
        # Draw ribbon as connected segments with varying width and alpha
        for i in range(len(points) - 1):
            # Calculate alpha based on position in trail
            alpha = (i + 1) / len(points)  # Newer points more opaque
            
            # Calculate width based on velocity
            velocity = trail[i]['velocity']
            width = max(1, int(2 + velocity * 0.3))
            
            # Apply turbulence for smoke effect
            turb_x = int(self.turbulence_amplitude * math.sin(self.turbulence_time + i * 0.2))
            turb_y = int(self.turbulence_amplitude * math.cos(self.turbulence_time + i * 0.3))
            
            pt1 = (points[i][0] + turb_x, points[i][1] + turb_y)
            pt2 = (points[i + 1][0] + turb_x, points[i + 1][1] + turb_y)
            
            # Adjust color based on alpha
            adjusted_color = tuple(int(c * alpha) for c in color)
            
            # Draw ribbon segment
            cv2.line(canvas, pt1, pt2, adjusted_color, width)
            
            # Add glow effect for newer segments
            if alpha > 0.5:
                glow_color = tuple(int(c * alpha * 0.3) for c in color)
                cv2.line(canvas, pt1, pt2, glow_color, width + 2)
                
    def _draw_current_joints(self, canvas: np.ndarray, landmarks: List[Dict]):
        """Draw current joint positions as glowing points"""
        for joint_name, landmark_idx in self.joint_indices.items():
            if landmark_idx < len(landmarks):
                landmark = landmarks[landmark_idx]
                x = int(landmark['x'] * self.width)
                y = int(landmark['y'] * self.height)
                color = self.ribbon_colors[joint_name]
                
                # Draw glowing joint
                # Outer glow
                glow_color = tuple(c // 3 for c in color)
                cv2.circle(canvas, (x, y), 8, glow_color, -1)
                # Main circle
                cv2.circle(canvas, (x, y), 5, color, -1)
                # White center
                cv2.circle(canvas, (x, y), 2, (255, 255, 255), -1)
                
    def _draw_bezier_curve(self, canvas: np.ndarray, points: List[Tuple[int, int]], 
                          color: Tuple[int, int, int], alpha: float, width: int):
        """Draw smooth bezier curve through points"""
        if len(points) < 3:
            # Just draw straight line for 2 points
            if len(points) == 2:
                adjusted_color = tuple(int(c * alpha) for c in color)
                cv2.line(canvas, points[0], points[1], adjusted_color, width)
            return
            
        # Generate bezier curve points
        curve_points = []
        num_segments = 20
        
        for i in range(num_segments + 1):
            t = i / num_segments
            point = self._bezier_point(points, t)
            curve_points.append(point)
            
        # Draw the curve
        adjusted_color = tuple(int(c * alpha) for c in color)
        for i in range(len(curve_points) - 1):
            cv2.line(canvas, curve_points[i], curve_points[i + 1], adjusted_color, width)
            
    def _bezier_point(self, points: List[Tuple[int, int]], t: float) -> Tuple[int, int]:
        """Calculate point on bezier curve at parameter t"""
        if len(points) == 1:
            return points[0]
        elif len(points) == 2:
            x = int((1 - t) * points[0][0] + t * points[1][0])
            y = int((1 - t) * points[0][1] + t * points[1][1])
            return (x, y)
        else:
            # Recursive bezier calculation
            new_points = []
            for i in range(len(points) - 1):
                x = int((1 - t) * points[i][0] + t * points[i + 1][0])
                y = int((1 - t) * points[i][1] + t * points[i + 1][1])
                new_points.append((x, y))
            return self._bezier_point(new_points, t)
            
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw message when no person is detected"""
        text = "Move to create silk trails"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(canvas, text, (text_x, text_y), font, 1.0, (200, 150, 255), 2)
        
    def reset(self):
        """Reset filter state"""
        for trail in self.joint_trails.values():
            trail.clear()
        self.turbulence_time = 0
        
    def set_intensity(self, intensity: float):
        """Set filter intensity"""
        super().set_intensity(intensity)
        # Adjust trail length and turbulence based on intensity
        self.trail_length = int(20 + 40 * intensity)
        for trail in self.joint_trails.values():
            trail = deque(list(trail)[-self.trail_length:], maxlen=self.trail_length)
        self.turbulence_amplitude = 2.0 + 8.0 * intensity
