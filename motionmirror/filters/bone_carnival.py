"""
Filter 3: Bone Carnival
Halloween cartoon skeleton on black background
"""

import numpy as np
import cv2
import math
from typing import List, Dict, Tuple
from .base_filter import BaseFilter


class BoneCarnivalFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Cartoon bone colors
        self.bone_colors = {
            'skull': (255, 255, 200),      # Bone white
            'spine': (200, 100, 255),      # Purple
            'ribcage': (150, 255, 150),    # Lime green
            'arms': (255, 200, 100),       # Orange
            'legs': (100, 200, 255),       # Light blue
            'joints': (255, 150, 50)        # Orange joints
        }
        
        # Animation
        self.wobble_time = 0
        self.flicker_time = 0
        
        # Ambient decorations
        self.bats = []
        self.stars = []
        self._init_ambient_decorations()
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply bone carnival filter"""
        canvas = self.create_black_canvas()
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Update animations
        self.wobble_time += 0.15
        self.flicker_time += 0.08
        
        # Calculate movement for wobble effect
        movement_intensity = self._calculate_movement_intensity(velocities)
        
        # Draw skeleton parts
        self._draw_skull(canvas, landmarks, movement_intensity)
        self._draw_spine(canvas, landmarks, movement_intensity)
        self._draw_ribcage(canvas, landmarks, movement_intensity)
        self._draw_arms(canvas, landmarks, movement_intensity)
        self._draw_legs(canvas, landmarks, movement_intensity)
        self._draw_joints(canvas, landmarks, movement_intensity)
        
        # Draw ambient decorations
        self._draw_ambient_decorations(canvas)
        
        # Apply flickering effect
        canvas = self._apply_flicker(canvas)
        
        return canvas
        
    def _calculate_movement_intensity(self, velocities: List[Dict]) -> float:
        """Calculate movement intensity for wobble effect"""
        if not velocities:
            return 0.1
            
        total_velocity = sum(v.get('magnitude', 0) for v in velocities)
        return min(1.0, total_velocity / 100.0)
        
    def _get_wobble_offset(self, intensity: float, index: int = 0) -> Tuple[float, float]:
        """Get wobble offset for animation"""
        wobble_amount = intensity * 5.0
        x_offset = wobble_amount * math.sin(self.wobble_time + index * 0.5)
        y_offset = wobble_amount * math.cos(self.wobble_time + index * 0.3)
        return x_offset, y_offset
        
    def _draw_skull(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw cartoon skull at head position"""
        if len(landmarks) < 10:
            return
            
        # Use nose and eye landmarks for skull position
        nose = landmarks[0]
        left_eye = landmarks[2]
        right_eye = landmarks[5]
        
        # Calculate skull center and size
        center_x = int(nose['x'] * self.width)
        center_y = int(nose['y'] * self.height)
        
        eye_distance = abs(left_eye['x'] - right_eye['x']) * self.width
        skull_radius = int(eye_distance * 1.5)
        
        # Apply wobble
        wobble_x, wobble_y = self._get_wobble_offset(movement, 0)
        center_x += int(wobble_x)
        center_y += int(wobble_y)
        
        # Draw skull (circle)
        cv2.circle(canvas, (center_x, center_y), skull_radius, 
                  self.bone_colors['skull'], -1)
        
        # Draw eyes (dark circles)
        eye_radius = skull_radius // 6
        left_eye_x = int(left_eye['x'] * self.width) + int(wobble_x)
        left_eye_y = int(left_eye['y'] * self.height) + int(wobble_y)
        right_eye_x = int(right_eye['x'] * self.width) + int(wobble_x)
        right_eye_y = int(right_eye['y'] * self.height) + int(wobble_y)
        
        cv2.circle(canvas, (left_eye_x, left_eye_y), eye_radius, (0, 0, 0), -1)
        cv2.circle(canvas, (right_eye_x, right_eye_y), eye_radius, (0, 0, 0), -1)
        
        # Draw mouth (jagged line)
        mouth_y = center_y + skull_radius // 2
        mouth_width = skull_radius
        for i in range(5):
            x = center_x - mouth_width//2 + i * mouth_width//4
            y = mouth_y + (i % 2) * 10
            cv2.line(canvas, (x, y), (x + mouth_width//8, y + 10), (0, 0, 0), 3)
            
    def _draw_spine(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw cartoon spine"""
        spine_points = [0, 11, 23, 24, 12]  # Nose to shoulders to hips
        
        for i in range(len(spine_points) - 1):
            if spine_points[i] < len(landmarks) and spine_points[i+1] < len(landmarks):
                pt1 = landmarks[spine_points[i]]
                pt2 = landmarks[spine_points[i+1]]
                
                x1 = int(pt1['x'] * self.width)
                y1 = int(pt1['y'] * self.height)
                x2 = int(pt2['x'] * self.width)
                y2 = int(pt2['y'] * self.height)
                
                # Apply wobble
                wobble_x, wobble_y = self._get_wobble_offset(movement, i)
                x1 += int(wobble_x)
                y1 += int(wobble_y)
                x2 += int(wobble_x)
                y2 += int(wobble_y)
                
                # Draw thick spine bone
                cv2.line(canvas, (x1, y1), (x2, y2), self.bone_colors['spine'], 8)
                
    def _draw_ribcage(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw cartoon ribcage"""
        # Shoulder and hip landmarks
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Apply wobble
        wobble_x, wobble_y = self._get_wobble_offset(movement, 5)
        
        # Convert to coordinates
        ls_x = int(left_shoulder['x'] * self.width) + int(wobble_x)
        ls_y = int(left_shoulder['y'] * self.height) + int(wobble_y)
        rs_x = int(right_shoulder['x'] * self.width) + int(wobble_x)
        rs_y = int(right_shoulder['y'] * self.height) + int(wobble_y)
        lh_x = int(left_hip['x'] * self.width) + int(wobble_x)
        lh_y = int(left_hip['y'] * self.height) + int(wobble_y)
        rh_x = int(right_hip['x'] * self.width) + int(wobble_x)
        rh_y = int(right_hip['y'] * self.height) + int(wobble_y)
        
        # Draw ribcage as curved lines
        center_x = (ls_x + rs_x) // 2
        
        # Top rib
        cv2.line(canvas, (ls_x, ls_y), (center_x, ls_y + 20), self.bone_colors['ribcage'], 6)
        cv2.line(canvas, (rs_x, rs_y), (center_x, rs_y + 20), self.bone_colors['ribcage'], 6)
        
        # Middle ribs
        mid_y = (ls_y + lh_y) // 2
        cv2.line(canvas, (ls_x + 10, mid_y), (center_x, mid_y), self.bone_colors['ribcage'], 5)
        cv2.line(canvas, (rs_x - 10, mid_y), (center_x, mid_y), self.bone_colors['ribcage'], 5)
        
        # Bottom ribs
        cv2.line(canvas, (ls_x + 20, lh_y - 20), (center_x, lh_y - 10), self.bone_colors['ribcage'], 4)
        cv2.line(canvas, (rs_x - 20, rh_y - 20), (center_x, rh_y - 10), self.bone_colors['ribcage'], 4)
        
    def _draw_arms(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw cartoon arm bones"""
        arm_connections = [
            (11, 13), (13, 15),  # Left arm
            (12, 14), (14, 16)   # Right arm
        ]
        
        for i, connection in enumerate(arm_connections):
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                x1 = int(pt1['x'] * self.width)
                y1 = int(pt1['y'] * self.height)
                x2 = int(pt2['x'] * self.width)
                y2 = int(pt2['y'] * self.height)
                
                # Apply wobble
                wobble_x, wobble_y = self._get_wobble_offset(movement, i + 10)
                x1 += int(wobble_x)
                y1 += int(wobble_y)
                x2 += int(wobble_x)
                y2 += int(wobble_y)
                
                # Draw thick bone
                cv2.line(canvas, (x1, y1), (x2, y2), self.bone_colors['arms'], 6)
                
    def _draw_legs(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw cartoon leg bones"""
        leg_connections = [
            (23, 25), (25, 27), (27, 29),  # Left leg
            (24, 26), (26, 28), (28, 30)   # Right leg
        ]
        
        for i, connection in enumerate(leg_connections):
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                x1 = int(pt1['x'] * self.width)
                y1 = int(pt1['y'] * self.height)
                x2 = int(pt2['x'] * self.width)
                y2 = int(pt2['y'] * self.height)
                
                # Apply wobble
                wobble_x, wobble_y = self._get_wobble_offset(movement, i + 20)
                x1 += int(wobble_x)
                y1 += int(wobble_y)
                x2 += int(wobble_x)
                y2 += int(wobble_y)
                
                # Draw thick bone
                cv2.line(canvas, (x1, y1), (x2, y2), self.bone_colors['legs'], 7)
                
    def _draw_joints(self, canvas: np.ndarray, landmarks: List[Dict], movement: float):
        """Draw colorful joints"""
        joint_indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        
        for i, idx in enumerate(joint_indices):
            if idx < len(landmarks):
                landmark = landmarks[idx]
                x = int(landmark['x'] * self.width)
                y = int(landmark['y'] * self.height)
                
                # Apply wobble
                wobble_x, wobble_y = self._get_wobble_offset(movement, i + 30)
                x += int(wobble_x)
                y += int(wobble_y)
                
                # Draw oversized colorful joint
                cv2.circle(canvas, (x, y), 12, self.bone_colors['joints'], -1)
                cv2.circle(canvas, (x, y), 8, (255, 255, 255), -1)
                
    def _init_ambient_decorations(self):
        """Initialize bats and stars"""
        # Create bats
        for _ in range(5):
            self.bats.append({
                'x': np.random.randint(0, self.width),
                'y': np.random.randint(0, self.height // 2),
                'vx': np.random.uniform(-1, 1),
                'vy': np.random.uniform(-0.5, 0.5),
                'phase': np.random.uniform(0, 2 * math.pi)
            })
            
        # Create stars
        for _ in range(20):
            self.stars.append({
                'x': np.random.randint(0, self.width),
                'y': np.random.randint(0, self.height),
                'brightness': np.random.uniform(0.3, 1.0),
                'phase': np.random.uniform(0, 2 * math.pi)
            })
            
    def _draw_ambient_decorations(self, canvas: np.ndarray):
        """Draw bats and stars"""
        # Update and draw bats
        for bat in self.bats:
            # Update position
            bat['x'] += bat['vx']
            bat['y'] += bat['vy']
            bat['phase'] += 0.1
            
            # Wrap around screen
            if bat['x'] < 0:
                bat['x'] = self.width
            elif bat['x'] > self.width:
                bat['x'] = 0
            if bat['y'] < 0:
                bat['y'] = self.height // 2
            elif bat['y'] > self.height // 2:
                bat['y'] = 0
                
            # Draw simple bat shape
            x, y = int(bat['x']), int(bat['y'])
            wing_flap = int(5 * math.sin(bat['phase']))
            
            # Body
            cv2.ellipse(canvas, (x, y), (3, 6), 0, 0, 360, (50, 50, 50), -1)
            # Wings
            cv2.ellipse(canvas, (x - 5, y), (8, 3), -30 + wing_flap, 0, 180, (50, 50, 50), -1)
            cv2.ellipse(canvas, (x + 5, y), (8, 3), 30 - wing_flap, 0, 180, (50, 50, 50), -1)
            
        # Draw stars
        for star in self.stars:
            star['phase'] += 0.05
            brightness = int(100 * star['brightness'] * (0.7 + 0.3 * math.sin(star['phase'])))
            cv2.circle(canvas, (int(star['x']), int(star['y'])), 1, (brightness, brightness, brightness), -1)
            
    def _apply_flicker(self, canvas: np.ndarray) -> np.ndarray:
        """Apply candlelight flicker effect"""
        flicker_intensity = 0.9 + 0.1 * math.sin(self.flicker_time)
        return cv2.convertScaleAbs(canvas, alpha=flicker_intensity, beta=0)
        
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw Halloween-themed message"""
        text = "Step into the carnival..."
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.8, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(canvas, text, (text_x, text_y), font, 0.8, (255, 200, 100), 2)
        
    def reset(self):
        """Reset filter state"""
        self.wobble_time = 0
        self.flicker_time = 0
        self._init_ambient_decorations()
