import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.drawing import hsv_to_rgb

class PhantomEchoFilter:
    def __init__(self):
        self.name = "PHANTOM ECHO"
        self.icon = "👥"
        self.pose_buffer = []
        self.max_buffer_size = 12
        self.echo_intensity = 12  # Default number of ghost frames
        
    def add_pose_to_buffer(self, landmarks):
        """Add current pose to circular buffer"""
        if landmarks:
            self.pose_buffer.append(landmarks.copy())
            if len(self.pose_buffer) > self.max_buffer_size:
                self.pose_buffer.pop(0)
    
    def set_echo_intensity(self, intensity):
        """Set number of echo frames (5-20)"""
        self.echo_intensity = max(5, min(20, intensity))
    
    def get_hsv_color(self, time_offset):
        """Get color that shifts over time"""
        # Full spectrum cycle every 5 seconds
        hue = (time_offset / 5.0) % 1.0
        return hsv_to_rgb(hue, 1.0, 1.0)
    
    def draw_skeleton(self, canvas, landmarks, color, alpha, width, height):
        """Draw skeleton with given color and alpha"""
        if not landmarks:
            return
        
        # Convert normalized landmarks to pixel coordinates
        points = []
        for landmark in landmarks:
            x = int(landmark['x'] * width)
            y = int(landmark['y'] * height)
            points.append((x, y))
        
        # Define pose connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),  # Face
            (9, 10),  # Mouth
            (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),  # Left arm
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),  # Right arm
            (11, 23), (12, 24), (23, 24),  # Torso
            (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),  # Left leg
            (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)   # Right leg
        ]
        
        # Create overlay for alpha blending
        overlay = canvas.copy()
        
        # Draw connections
        for connection in connections:
            if connection[0] < len(points) and connection[1] < len(points):
                pt1 = points[connection[0]]
                pt2 = points[connection[1]]
                cv2.line(overlay, pt1, pt2, color, 2)
        
        # Draw joints
        for point in points:
            cv2.circle(overlay, point, 3, color, -1)
        
        # Blend with alpha
        cv2.addWeighted(canvas, 1.0, overlay, alpha / 255.0, 0, canvas)
    
    def apply(self, frame, landmarks, width, height):
        """Apply phantom echo filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if landmarks:
            # Add current pose to buffer
            self.add_pose_to_buffer(landmarks)
        
        # Get current time for color shifting
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        # Draw ghost echoes
        num_echoes = min(len(self.pose_buffer), self.echo_intensity)
        for i in range(num_echoes):
            # Calculate opacity based on age (oldest = 5%, newest = 80%)
            opacity = int(5 + (75 * i / max(1, num_echoes - 1)))
            
            # Get shifting color for this echo
            color = self.get_hsv_color(current_time + i * 0.1)
            
            # Draw the echo
            self.draw_skeleton(canvas, self.pose_buffer[i], color, opacity, width, height)
        
        # Draw current live pose solid white on top
        if landmarks:
            self.draw_skeleton(canvas, landmarks, (255, 255, 255), 255, width, height)
        
        return canvas
