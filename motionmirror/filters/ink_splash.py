import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.drawing import draw_ink_splash

class InkSplashFilter:
    def __init__(self):
        self.name = "INK SPLASH"
        self.icon = "🥊"
        
        # Ink colors
        self.ink_colors = {
            'left_punch': (0, 102, 255),    # Electric blue
            'right_punch': (255, 26, 26),   # Crimson red
            'left_kick': (0, 255, 100),     # Green
            'right_kick': (255, 255, 0)     # Yellow
        }
        
        # Track previous landmarks for movement detection
        self.prev_landmarks = None
        
        # Persistent ink marks on canvas
        self.ink_marks = []
        
        # Combo tracking
        self.combo_count = 0
        self.last_action_time = 0
        self.combo_reset_time = 2.0  # Reset combo after 2 seconds
        
    def detect_punch(self, wrist_idx, elbow_idx, landmarks, width, height):
        """Detect punch gesture from wrist and elbow landmarks"""
        if len(landmarks) <= max(wrist_idx, elbow_idx) or not self.prev_landmarks:
            return False, 0, 0
        
        # Get current and previous positions
        curr_wrist = landmarks[wrist_idx]
        prev_wrist = self.prev_landmarks[wrist_idx]
        curr_elbow = landmarks[elbow_idx]
        
        # Calculate movement
        dx = (curr_wrist['x'] - prev_wrist['x']) * width
        dy = (curr_wrist['y'] - prev_wrist['y']) * height
        movement = math.sqrt(dx**2 + dy**2)
        
        # Check if it's a rapid forward movement
        if movement > 25:  # Threshold for punch detection
            # Calculate punch direction from elbow to wrist
            dir_x = curr_wrist['x'] - curr_elbow['x']
            dir_y = curr_wrist['y'] - curr_elbow['y']
            direction = math.atan2(dir_y, dir_x)
            
            return True, direction, movement
        
        return False, 0, 0
    
    def detect_kick(self, ankle_idx, knee_idx, landmarks, width, height):
        """Detect kick gesture from ankle and knee landmarks"""
        if len(landmarks) <= max(ankle_idx, knee_idx) or not self.prev_landmarks:
            return False, 0, 0
        
        # Get current and previous positions
        curr_ankle = landmarks[ankle_idx]
        prev_ankle = self.prev_landmarks[ankle_idx]
        
        # Calculate movement
        dx = (curr_ankle['x'] - prev_ankle['x']) * width
        dy = (curr_ankle['y'] - prev_ankle['y']) * height
        movement = math.sqrt(dx**2 + dy**2)
        
        # Check if it's a rapid movement
        if movement > 20:  # Threshold for kick detection
            # Calculate kick direction
            dir_x = curr_ankle['x'] - prev_ankle['x']
            dir_y = curr_ankle['y'] - prev_ankle['y']
            direction = math.atan2(dir_y, dir_x)
            
            return True, direction, movement
        
        return False, 0, 0
    
    def add_ink_splash(self, canvas, x, y, direction, color, count=100):
        """Add ink splash effect at position"""
        # Emit ink droplets in a cone
        spread_angle = math.radians(40)  # 40 degree spread
        
        for _ in range(count):
            # Random angle within cone
            angle = direction + np.random.uniform(-spread_angle/2, spread_angle/2)
            
            # Random distance
            distance = np.random.uniform(10, 100)
            
            # Calculate target position
            target_x = x + math.cos(angle) * distance
            target_y = y + math.sin(angle) * distance
            
            # Draw ink splash at target
            draw_ink_splash(canvas, int(target_x), int(target_y), color, 
                          size_range=(4, 15))
        
        # Add persistent ink mark at origin
        self.ink_marks.append({
            'x': x, 'y': y, 'color': color, 
            'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
        })
    
    def update_combo(self):
        """Update combo counter"""
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        # Reset combo if too much time has passed
        if current_time - self.last_action_time > self.combo_reset_time:
            self.combo_count = 0
        
        self.combo_count += 1
        self.last_action_time = current_time
    
    def draw_combo_text(self, canvas):
        """Draw combo counter on canvas"""
        if self.combo_count >= 3:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"COMBO x{self.combo_count}"
            
            # Text properties
            font_scale = 1.5
            thickness = 3
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Position at top center
            x = (canvas.shape[1] - text_width) // 2
            y = 80
            
            # Draw text with shadow effect
            cv2.putText(canvas, text, (x+2, y+2), font, font_scale, (0, 0, 0), thickness)
            cv2.putText(canvas, text, (x, y), font, font_scale, (255, 255, 255), thickness)
    
    def apply(self, frame, landmarks, width, height):
        """Apply ink splash filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if not landmarks:
            return canvas
        
        # Draw persistent ink marks (fade over 3 seconds)
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        self.ink_marks = [mark for mark in self.ink_marks 
                         if current_time - mark['timestamp'] < 3.0]
        
        for mark in self.ink_marks:
            age = current_time - mark['timestamp']
            alpha = max(0, 1 - age / 3.0)  # Fade over 3 seconds
            
            # Draw fading ink mark
            faded_color = tuple(int(c * alpha) for c in mark['color'])
            draw_ink_splash(canvas, mark['x'], mark['y'], faded_color, 
                          size_range=(6, 20))
        
        # Detect punches and kicks
        actions_detected = 0
        
        # Left punch
        is_punch, direction, movement = self.detect_punch(15, 13, landmarks, width, height)
        if is_punch:
            wrist_x = int(landmarks[15]['x'] * width)
            wrist_y = int(landmarks[15]['y'] * height)
            self.add_ink_splash(canvas, wrist_x, wrist_y, direction, 
                              self.ink_colors['left_punch'], count=80)
            actions_detected += 1
        
        # Right punch
        is_punch, direction, movement = self.detect_punch(16, 14, landmarks, width, height)
        if is_punch:
            wrist_x = int(landmarks[16]['x'] * width)
            wrist_y = int(landmarks[16]['y'] * height)
            self.add_ink_splash(canvas, wrist_x, wrist_y, direction, 
                              self.ink_colors['right_punch'], count=80)
            actions_detected += 1
        
        # Left kick
        is_kick, direction, movement = self.detect_kick(27, 25, landmarks, width, height)
        if is_kick:
            ankle_x = int(landmarks[27]['x'] * width)
            ankle_y = int(landmarks[27]['y'] * height)
            self.add_ink_splash(canvas, ankle_x, ankle_y, direction, 
                              self.ink_colors['left_kick'], count=60)
            actions_detected += 1
        
        # Right kick
        is_kick, direction, movement = self.detect_kick(28, 26, landmarks, width, height)
        if is_kick:
            ankle_x = int(landmarks[28]['x'] * width)
            ankle_y = int(landmarks[28]['y'] * height)
            self.add_ink_splash(canvas, ankle_x, ankle_y, direction, 
                              self.ink_colors['right_kick'], count=60)
            actions_detected += 1
        
        # Update combo if actions detected
        if actions_detected > 0:
            self.update_combo()
        
        # Draw combo counter
        self.draw_combo_text(canvas)
        
        # Store current landmarks for next frame
        self.prev_landmarks = landmarks.copy()
        
        return canvas
    
    def clear_canvas(self):
        """Clear persistent ink marks"""
        self.ink_marks.clear()
        self.combo_count = 0
