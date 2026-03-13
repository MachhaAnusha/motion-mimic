"""
Filter 4: Echo Walker
Motion echo / ghost trail art with time-lapse effect
"""

import numpy as np
import cv2
import time
from typing import List, Dict, Tuple
from collections import deque
from .base_filter import BaseFilter


class EchoWalkerFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Ghost trail storage
        self.max_trail_length = 15
        self.pose_history = deque(maxlen=self.max_trail_length)
        
        # Color gradient for ghosts (newest to oldest)
        self.ghost_colors = [
            (255, 255, 255),  # White (newest)
            (200, 200, 255),  # Light blue
            (150, 150, 255),  # Blue
            (100, 100, 200),  # Dark blue
            (50, 50, 150),    # Deep blue
            (25, 25, 100)     # Very deep blue (oldest)
        ]
        
        # Movement detection
        self.last_movement_time = time.time()
        self.movement_threshold = 2.0
        self.no_movement_prompt_time = 3.0  # Show prompt after 3 seconds of no movement
        
        # Pose connections for skeleton drawing
        self.pose_connections = [
            (11, 12), (11, 23), (12, 24), (23, 24),  # Torso
            (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
            (23, 25), (25, 27), (24, 26), (26, 28),  # Legs
            (15, 17), (15, 19), (15, 21),           # Left hand
            (16, 18), (16, 20), (16, 22),           # Right hand
            (27, 29), (27, 31), (28, 30), (28, 32)  # Feet
        ]
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply echo walker filter"""
        canvas = self.create_black_canvas()
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Check for movement
        current_movement = self._calculate_movement(velocities)
        if current_movement > self.movement_threshold:
            self.last_movement_time = time.time()
            
        # Add current pose to history
        self.pose_history.append({
            'landmarks': landmarks.copy(),
            'timestamp': time.time(),
            'movement': current_movement
        })
        
        # Draw ghost trails
        self._draw_ghost_trails(canvas)
        
        # Draw current pose
        self._draw_current_pose(canvas, landmarks)
        
        # Show dancing prompt if no movement
        if time.time() - self.last_movement_time > self.no_movement_prompt_time:
            self._draw_dancing_prompt(canvas)
            
        return canvas
        
    def _calculate_movement(self, velocities: List[Dict]) -> float:
        """Calculate overall movement intensity"""
        if not velocities:
            return 0.0
            
        return sum(v.get('magnitude', 0) for v in velocities)
        
    def _get_ghost_color_and_alpha(self, age_index: int) -> Tuple[Tuple[int, int, int], float]:
        """Get color and alpha for ghost based on age"""
        # Map age to color gradient
        color_index = min(age_index * len(self.ghost_colors) // self.max_trail_length, 
                         len(self.ghost_colors) - 1)
        color = self.ghost_colors[color_index]
        
        # Calculate alpha (newer ghosts are more opaque)
        alpha = max(0.05, 0.4 * (1.0 - age_index / self.max_trail_length))
        
        return color, alpha
        
    def _draw_ghost_trails(self, canvas: np.ndarray):
        """Draw historical poses as ghost trails"""
        for i, pose_data in enumerate(self.pose_history):
            age_index = len(self.pose_history) - i - 1  # 0 = newest, higher = older
            
            if age_index == 0:  # Skip current pose
                continue
                
            color, alpha = self._get_ghost_color_and_alpha(age_index)
            landmarks = pose_data['landmarks']
            
            # Draw ghost skeleton
            self._draw_skeleton(canvas, landmarks, color, alpha)
            
    def _draw_skeleton(self, canvas: np.ndarray, landmarks: List[Dict], 
                      color: Tuple[int, int, int], alpha: float):
        """Draw skeleton with specific color and alpha"""
        # Draw connections
        for connection in self.pose_connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                x1, y1 = int(pt1['x'] * self.width), int(pt1['y'] * self.height)
                x2, y2 = int(pt2['x'] * self.width), int(pt2['y'] * self.height)
                
                # Apply alpha by blending with black background
                adjusted_color = tuple(int(c * alpha) for c in color)
                cv2.line(canvas, (x1, y1), (x2, y2), adjusted_color, 2)
                
        # Draw joints
        for landmark in landmarks:
            if landmark['visibility'] > 0.3:
                x, y = int(landmark['x'] * self.width), int(landmark['y'] * self.height)
                adjusted_color = tuple(int(c * alpha) for c in color)
                cv2.circle(canvas, (x, y), 3, adjusted_color, -1)
                
    def _draw_current_pose(self, canvas: np.ndarray, landmarks: List[Dict]):
        """Draw the current pose with full opacity"""
        self._draw_skeleton(canvas, landmarks, (255, 255, 255), 1.0)
        
    def _draw_dancing_prompt(self, canvas: np.ndarray):
        """Draw prompt encouraging user to dance"""
        prompts = [
            "Start Dancing!",
            "Move Your Body!",
            "Dance Like Nobody's Watching!",
            "Feel the Music!",
            "Let Your Spirit Move!"
        ]
        
        # Cycle through prompts
        prompt_index = int(time.time()) % len(prompts)
        text = prompts[prompt_index]
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.2, 3)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        # Glowing text effect
        for i in range(3):
            alpha = 0.3 + 0.2 * math.sin(time.time() * 3 + i)
            color = tuple(int(255 * alpha) for _ in range(3))
            thickness = 5 - i
            cv2.putText(canvas, text, (text_x, text_y), font, 1.2, color, thickness)
            
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw message when no person is detected"""
        text = "Step into frame to create echoes"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(canvas, text, (text_x, text_y), font, 1.0, (200, 200, 255), 2)
        
    def reset(self):
        """Reset filter state"""
        self.pose_history.clear()
        self.last_movement_time = time.time()
        
    def set_intensity(self, intensity: float):
        """Set filter intensity"""
        super().set_intensity(intensity)
        # Adjust trail length based on intensity
        self.max_trail_length = int(10 + 15 * intensity)
        self.pose_history = deque(list(self.pose_history)[-self.max_trail_length:], 
                                 maxlen=self.max_trail_length)
