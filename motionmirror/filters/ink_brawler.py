"""
Filter 6: Ink Brawler
Shadow boxing → ink explosion on punch with canvas painting effect
"""

import numpy as np
import cv2
import math
import random
from typing import List, Dict, Tuple
from .base_filter import BaseFilter


class InkBrawlerFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Ink colors
        self.ink_colors = {
            'red': (200, 50, 50),
            'black': (50, 50, 50),
            'blue': (50, 100, 200)
        }
        self.current_ink_color = 'red'
        
        # Canvas for persistent ink effects
        self.ink_canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Ink splatter storage
        self.ink_splatters = []
        self.shockwaves = []
        
        # Punch detection settings
        self.punch_threshold = 15.0
        self.kick_threshold = 12.0
        
        # Body outline settings
        self.body_color = (80, 80, 80)
        
        # Pose connections for body outline
        self.pose_connections = [
            (11, 12), (11, 23), (12, 24), (23, 24),  # Torso
            (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
            (23, 25), (25, 27), (24, 26), (26, 28),  # Legs
            (15, 17), (15, 19), (15, 21),           # Left hand
            (16, 18), (16, 20), (16, 22)            # Right hand
        ]
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply ink brawler filter"""
        canvas = self.create_black_canvas()
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Detect punches and kicks
        gestures = self._detect_combat_gestures(landmarks, velocities)
        
        # Create ink effects for detected gestures
        if gestures['punch_left'] or gestures['punch_right']:
            self._create_punch_effect(landmarks, gestures)
        if gestures['kick_left'] or gestures['kick_right']:
            self._create_kick_effect(landmarks, gestures)
            
        # Update and draw ink effects
        self._update_ink_effects()
        
        # Draw persistent ink canvas
        canvas = cv2.add(canvas, self.ink_canvas)
        
        # Draw current ink splatters
        self._draw_ink_splatters(canvas)
        
        # Draw shockwaves
        self._draw_shockwaves(canvas)
        
        # Draw body outline
        self._draw_body_outline(canvas, landmarks)
        
        return canvas
        
    def _detect_combat_gestures(self, landmarks: List[Dict], 
                              velocities: List[Dict]) -> Dict[str, bool]:
        """Detect punch and kick gestures"""
        gestures = {
            'punch_left': False,
            'punch_right': False,
            'kick_left': False,
            'kick_right': False
        }
        
        if not velocities or len(landmarks) < 33:
            return gestures
            
        # Check wrist velocities for punches
        left_wrist_idx = 15
        right_wrist_idx = 16
        left_ankle_idx = 27
        right_ankle_idx = 28
        
        # Punch detection
        if left_wrist_idx < len(velocities):
            if velocities[left_wrist_idx].get('magnitude', 0) > self.punch_threshold:
                gestures['punch_left'] = True
                
        if right_wrist_idx < len(velocities):
            if velocities[right_wrist_idx].get('magnitude', 0) > self.punch_threshold:
                gestures['punch_right'] = True
                
        # Kick detection
        if left_ankle_idx < len(velocities):
            if velocities[left_ankle_idx].get('magnitude', 0) > self.kick_threshold:
                gestures['kick_left'] = True
                
        if right_ankle_idx < len(velocities):
            if velocities[right_ankle_idx].get('magnitude', 0) > self.kick_threshold:
                gestures['kick_right'] = True
                
        return gestures
        
    def _create_punch_effect(self, landmarks: List[Dict], gestures: Dict[str, bool]):
        """Create ink splatter effect for punches"""
        ink_color = self.ink_colors[self.current_ink_color]
        
        if gestures['punch_left'] and 15 < len(landmarks):
            wrist = landmarks[15]
            x = int(wrist['x'] * self.width)
            y = int(wrist['y'] * self.height)
            self._create_ink_splatter(x, y, ink_color, is_punch=True)
            
        if gestures['punch_right'] and 16 < len(landmarks):
            wrist = landmarks[16]
            x = int(wrist['x'] * self.width)
            y = int(wrist['y'] * self.height)
            self._create_ink_splatter(x, y, ink_color, is_punch=True)
            
    def _create_kick_effect(self, landmarks: List[Dict], gestures: Dict[str, bool]):
        """Create ink splatter effect for kicks"""
        ink_color = self.ink_colors[self.current_ink_color]
        
        if gestures['kick_left'] and 27 < len(landmarks):
            ankle = landmarks[27]
            x = int(ankle['x'] * self.width)
            y = int(ankle['y'] * self.height)
            self._create_ink_splatter(x, y, ink_color, is_punch=False)
            
        if gestures['kick_right'] and 28 < len(landmarks):
            ankle = landmarks[28]
            x = int(ankle['x'] * self.width)
            y = int(ankle['y'] * self.height)
            self._create_ink_splatter(x, y, ink_color, is_punch=False)
            
    def _create_ink_splatter(self, x: int, y: int, color: Tuple[int, int, int], 
                           is_punch: bool = True):
        """Create ink splatter effect at position"""
        # Add main splatter to persistent canvas
        splatter_size = random.randint(30, 60) if is_punch else random.randint(20, 40)
        self._draw_splatter_on_canvas(x, y, splatter_size, color)
        
        # Add animated splatter particles
        num_particles = random.randint(15, 25) if is_punch else random.randint(10, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15) if is_punch else random.uniform(3, 10)
            
            particle = {
                'x': x,
                'y': y,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'size': random.randint(2, 8),
                'color': color,
                'lifetime': random.uniform(0.5, 1.5),
                'age': 0
            }
            self.ink_splatters.append(particle)
            
        # Add shockwave for punches
        if is_punch:
            shockwave = {
                'x': x,
                'y': y,
                'radius': 10,
                'max_radius': random.randint(80, 120),
                'color': color,
                'lifetime': 0.8,
                'age': 0
            }
            self.shockwaves.append(shockwave)
            
    def _draw_splatter_on_canvas(self, x: int, y: int, size: int, 
                                color: Tuple[int, int, int]):
        """Draw ink splatter on persistent canvas"""
        # Main blob
        cv2.circle(self.ink_canvas, (x, y), size, color, -1)
        
        # Random drips and splatters
        num_drips = random.randint(5, 12)
        for _ in range(num_drips):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(size * 0.5, size * 1.5)
            drip_x = int(x + distance * math.cos(angle))
            drip_y = int(y + distance * math.sin(angle))
            drip_size = random.randint(2, size // 2)
            
            # Draw drip with bezier-like shape
            cv2.circle(self.ink_canvas, (drip_x, drip_y), drip_size, color, -1)
            
            # Connect to main blob with thin line
            cv2.line(self.ink_canvas, (x, y), (drip_x, drip_y), color, 1)
            
    def _update_ink_effects(self):
        """Update animated ink effects"""
        # Update splatter particles
        self.ink_splatters = [p for p in self.ink_splatters if p['age'] < p['lifetime']]
        for particle in self.ink_splatters:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.5  # Gravity
            particle['vx'] *= 0.95  # Friction
            particle['age'] += 0.016  # ~60 FPS
            
        # Update shockwaves
        self.shockwaves = [s for s in self.shockwaves if s['age'] < s['lifetime']]
        for shockwave in self.shockwaves:
            shockwave['radius'] += 3
            shockwave['age'] += 0.016
            
    def _draw_ink_splatters(self, canvas: np.ndarray):
        """Draw animated ink splatter particles"""
        for particle in self.ink_splatters:
            alpha = 1.0 - (particle['age'] / particle['lifetime'])
            if alpha > 0:
                x, y = int(particle['x']), int(particle['y'])
                size = int(particle['size'] * alpha)
                color = tuple(int(c * alpha) for c in particle['color'])
                cv2.circle(canvas, (x, y), size, color, -1)
                
    def _draw_shockwaves(self, canvas: np.ndarray):
        """Draw shockwave rings"""
        for shockwave in self.shockwaves:
            alpha = 1.0 - (shockwave['age'] / shockwave['lifetime'])
            if alpha > 0:
                x, y = int(shockwave['x']), int(shockwave['y'])
                radius = int(shockwave['radius'])
                color = tuple(int(c * alpha) for c in shockwave['color'])
                cv2.circle(canvas, (x, y), radius, color, 2)
                
    def _draw_body_outline(self, canvas: np.ndarray, landmarks: List[Dict]):
        """Draw simple body outline"""
        # Draw connections
        for connection in self.pose_connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                x1 = int(pt1['x'] * self.width)
                y1 = int(pt1['y'] * self.height)
                x2 = int(pt2['x'] * self.width)
                y2 = int(pt2['y'] * self.height)
                
                cv2.line(canvas, (x1, y1), (x2, y2), self.body_color, 2)
                
        # Draw joints
        for landmark in landmarks:
            if landmark['visibility'] > 0.3:
                x = int(landmark['x'] * self.width)
                y = int(landmark['y'] * self.height)
                cv2.circle(canvas, (x, y), 3, self.body_color, -1)
                
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw message when no person is detected"""
        text = "Start shadow boxing!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(canvas, text, (text_x, text_y), font, 1.0, (150, 50, 50), 2)
        
    def clear_canvas(self):
        """Clear the persistent ink canvas"""
        self.ink_canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.ink_splatters.clear()
        self.shockwaves.clear()
        
    def set_ink_color(self, color_name: str):
        """Set the ink color"""
        if color_name in self.ink_colors:
            self.current_ink_color = color_name
            
    def reset(self):
        """Reset filter state"""
        self.clear_canvas()
        
    def set_intensity(self, intensity: float):
        """Set filter intensity"""
        super().set_intensity(intensity)
        # Adjust gesture thresholds based on intensity
        self.punch_threshold = 10.0 + 10.0 * intensity
        self.kick_threshold = 8.0 + 8.0 * intensity
