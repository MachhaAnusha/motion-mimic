import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.drawing import apply_scanline_effect

class CryptbornFilter:
    def __init__(self):
        self.name = "CRYPTBORN"
        self.icon = "💀"
        
        # Halloween color palette
        self.colors = {
            'bone': (232, 232, 208),      # Off-white bone
            'joints': (255, 107, 53),     # Halloween orange
            'eyes': (0, 255, 0),          # Eerie green
            'teeth': (255, 255, 255)      # Pure white
        }
        
    def draw_skull(self, canvas, head_landmarks, width, height):
        """Draw cartoon skull at head position"""
        if len(head_landmarks) < 10:
            return
        
        # Get head center from nose landmark
        nose = head_landmarks[0]
        center_x = int(nose['x'] * width)
        center_y = int(nose['y'] * height)
        skull_radius = 40
        
        # Draw skull outline
        cv2.circle(canvas, (center_x, center_y), skull_radius, 
                  self.colors['bone'], 3)
        
        # Fill skull
        cv2.circle(canvas, (center_x, center_y), skull_radius - 3, 
                  self.colors['bone'], -1)
        
        # Draw eye sockets
        eye_y = center_y - 10
        left_eye_x = center_x - 12
        right_eye_x = center_x + 12
        eye_radius = 8
        
        # Glowing eye sockets
        cv2.circle(canvas, (left_eye_x, eye_y), eye_radius, 
                  self.colors['eyes'], -1)
        cv2.circle(canvas, (right_eye_x, eye_y), eye_radius, 
                  self.colors['eyes'], -1)
        
        # Draw grinning teeth
        teeth_y = center_y + 10
        teeth_width = 30
        teeth_height = 8
        teeth_x = center_x - teeth_width // 2
        
        # Teeth outline
        cv2.rectangle(canvas, (teeth_x, teeth_y), 
                    (teeth_x + teeth_width, teeth_y + teeth_height),
                    self.colors['teeth'], 2)
        
        # Individual teeth
        tooth_width = teeth_width // 6
        for i in range(6):
            tooth_x = teeth_x + i * tooth_width
            cv2.line(canvas, (tooth_x, teeth_y), 
                    (tooth_x, teeth_y + teeth_height), 
                    self.colors['teeth'], 1)
    
    def draw_ribcage(self, canvas, torso_landmarks, width, height):
        """Draw cartoon ribcage"""
        if len(torso_landmarks) < 4:
            return
        
        # Get torso bounds
        shoulders = [torso_landmarks[11], torso_landmarks[12]]
        hips = [torso_landmarks[23], torso_landmarks[24]]
        
        shoulder_y = int((shoulders[0]['y'] + shoulders[1]['y']) / 2 * height)
        hip_y = int((hips[0]['y'] + hips[1]['y']) / 2 * height)
        center_x = int((shoulders[0]['x'] + shoulders[1]['x']) / 2 * width)
        
        ribcage_height = hip_y - shoulder_y
        ribcage_width = 60
        
        # Draw ribcage outline
        cv2.ellipse(canvas, (center_x, shoulder_y + ribcage_height // 2),
                   (ribcage_width // 2, ribcage_height // 2), 0, 0, 360,
                   self.colors['bone'], 3)
        
        # Draw individual ribs
        for i in range(6):
            rib_y = shoulder_y + (i + 1) * ribcage_height // 7
            rib_width = ribcage_width // 2 - i * 3
            
            # Left rib
            cv2.arc(canvas, (center_x - rib_width // 2, rib_y),
                   rib_width, 180, 360, self.colors['bone'], 2)
            # Right rib
            cv2.arc(canvas, (center_x + rib_width // 2, rib_y),
                   rib_width, 0, 180, self.colors['bone'], 2)
    
    def draw_spine(self, canvas, spine_landmarks, width, height):
        """Draw connected vertebrae dots for spine"""
        spine_points = [11, 12, 23, 24]  # Shoulders to hips
        
        for i in range(len(spine_points) - 1):
            if spine_points[i] < len(spine_landmarks) and spine_points[i+1] < len(spine_landmarks):
                pt1 = spine_landmarks[spine_points[i]]
                pt2 = spine_landmarks[spine_points[i+1]]
                
                x1 = int(pt1['x'] * width)
                y1 = int(pt1['y'] * height)
                x2 = int(pt2['x'] * width)
                y2 = int(pt2['y'] * height)
                
                # Draw vertebrae dots along the line
                num_dots = 5
                for j in range(num_dots):
                    t = j / (num_dots - 1)
                    dot_x = int(x1 + (x2 - x1) * t)
                    dot_y = int(y1 + (y2 - y1) * t)
                    cv2.circle(canvas, (dot_x, dot_y), 3, self.colors['bone'], -1)
    
    def draw_bone(self, canvas, pt1, pt2, width, height):
        """Draw cartoon bone between two points"""
        x1 = int(pt1['x'] * width)
        y1 = int(pt1['y'] * height)
        x2 = int(pt2['x'] * width)
        y2 = int(pt2['y'] * height)
        
        # Calculate bone thickness
        bone_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        thickness = max(6, int(bone_length / 10))
        
        # Draw main bone
        cv2.line(canvas, (x1, y1), (x2, y2), self.colors['bone'], thickness)
        
        # Draw joint knobs at ends
        cv2.circle(canvas, (x1, y1), thickness + 2, self.colors['joints'], -1)
        cv2.circle(canvas, (x2, y2), thickness + 2, self.colors['joints'], -1)
    
    def apply(self, frame, landmarks, width, height):
        """Apply cryptborn skeleton filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if not landmarks:
            return canvas
        
        # Draw skull
        self.draw_skull(canvas, landmarks, width, height)
        
        # Draw ribcage
        self.draw_ribcage(canvas, landmarks, width, height)
        
        # Draw spine
        self.draw_spine(canvas, landmarks, width, height)
        
        # Draw arm bones
        arm_connections = [
            (11, 13), (13, 15),  # Left arm
            (12, 14), (14, 16),  # Right arm
        ]
        
        for connection in arm_connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                self.draw_bone(canvas, landmarks[connection[0]], 
                             landmarks[connection[1]], width, height)
        
        # Draw leg bones
        leg_connections = [
            (23, 25), (25, 27),  # Left leg
            (24, 26), (26, 28),  # Right leg
        ]
        
        for connection in leg_connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                self.draw_bone(canvas, landmarks[connection[0]], 
                             landmarks[connection[1]], width, height)
        
        # Apply scanline flicker effect
        canvas = apply_scanline_effect(canvas, intensity=0.05)
        
        return canvas
