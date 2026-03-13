import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.particles import ParticleSystem
from utils.drawing import draw_glow_circle

class AuraFilter:
    def __init__(self):
        self.name = "AURA"
        self.icon = "✨"
        self.particle_system = ParticleSystem(max_particles=5000)
        self.prev_landmarks = None
        self.gesture_state = {
            'hands_raised': False,
            'arms_spread': False,
            'hands_hips': False,
            'last_gesture_time': 0
        }
        
    def detect_gestures(self, landmarks):
        """Detect specific gestures for special effects"""
        if len(landmarks) < 33:
            return None
        
        # Get key points
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        nose = landmarks[0]
        
        # Gesture 1: Both hands raised above head
        hands_raised = (left_wrist['y'] < nose['y'] and right_wrist['y'] < nose['y'])
        
        # Gesture 2: Arms spread wide
        arms_spread = (left_wrist['x'] < left_shoulder['x'] - 0.1 and 
                      right_wrist['x'] > right_shoulder['x'] + 0.1)
        
        # Gesture 3: Hands at hips, elbows out
        hands_hips = (abs(left_wrist['y'] - left_hip['y']) < 0.1 and 
                     abs(right_wrist['y'] - right_hip['y']) < 0.1 and
                     left_wrist['x'] < left_shoulder['x'] and 
                     right_wrist['x'] > right_shoulder['x'])
        
        # Determine which gesture is active
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        if hands_raised and not self.gesture_state['hands_raised']:
            self.gesture_state['hands_raised'] = True
            self.gesture_state['last_gesture_time'] = current_time
            return "SUPERNOVA"
        elif arms_spread and not self.gesture_state['arms_spread']:
            self.gesture_state['arms_spread'] = True
            self.gesture_state['last_gesture_time'] = current_time
            return "WAVE"
        elif hands_hips and not self.gesture_state['hands_hips']:
            self.gesture_state['hands_hips'] = True
            self.gesture_state['last_gesture_time'] = current_time
            return "PULSE"
        
        # Reset gesture states after 2 seconds
        if current_time - self.gesture_state['last_gesture_time'] > 2.0:
            self.gesture_state = {
                'hands_raised': False,
                'arms_spread': False,
                'hands_hips': False,
                'last_gesture_time': current_time
            }
        
        return None
    
    def apply(self, frame, landmarks, width, height):
        """Apply aura particle filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if not landmarks:
            return canvas
        
        # Detect gestures
        gesture = self.detect_gestures(landmarks)
        
        # Handle special gesture effects
        if gesture == "SUPERNOVA":
            # Burst from torso
            torso_x = int(landmarks[11]['x'] * width)
            torso_y = int(landmarks[11]['y'] * height)
            self.particle_system.emit_burst(torso_x, torso_y, count=500, 
                                           speed=8, color=(255, 255, 255))
        elif gesture == "WAVE":
            # Wave particles from body
            for landmark in landmarks:
                x = int(landmark['x'] * width)
                y = int(landmark['y'] * height)
                angle = math.atan2(y - height/2, x - width/2)
                self.particle_system.emit_cone(x, y, angle, spread_angle=60, 
                                              count=20, speed=3, color=(255, 100, 255))
        elif gesture == "PULSE":
            # Rhythmic pulse from body outline
            pulse_time = cv2.getTickCount() / cv2.getTickFrequency()
            if int(pulse_time * 2) % 2 == 0:  # Pulse every 0.5 seconds
                for landmark in landmarks:
                    x = int(landmark['x'] * width)
                    y = int(landmark['y'] * height)
                    self.particle_system.emit_burst(x, y, count=10, 
                                                   speed=2, color=(100, 255, 255))
        
        # Calculate movement speed for each landmark
        movement_speeds = []
        if self.prev_landmarks:
            for i, landmark in enumerate(landmarks):
                if i < len(self.prev_landmarks):
                    dx = (landmark['x'] - self.prev_landmarks[i]['x']) * width
                    dy = (landmark['y'] - self.prev_landmarks[i]['y']) * height
                    speed = math.sqrt(dx**2 + dy**2)
                    movement_speeds.append(speed)
                else:
                    movement_speeds.append(0)
        else:
            movement_speeds = [0] * len(landmarks)
        
        # Emit particles based on movement
        for i, (landmark, speed) in enumerate(zip(landmarks, movement_speeds)):
            x = int(landmark['x'] * width)
            y = int(landmark['y'] * height)
            
            if speed < 5:  # Slow motion
                color = (0, 255, 200)  # Cyan/teal
                self.particle_system.emit(x, y, vx=0, vy=1, color=color, 
                                        count=2, lifetime=60, size=3)
            elif speed < 15:  # Medium motion
                color = (255, 100, 255)  # Purple/pink
                angle = math.atan2(speed, 1)
                vx = math.cos(angle) * 2
                vy = math.sin(angle) * 2
                self.particle_system.emit(x, y, vx=vx, vy=vy, color=color, 
                                        count=3, lifetime=45, size=4)
            else:  # Fast motion
                color = (255, 255, 100)  # White/yellow
                self.particle_system.emit_burst(x, y, count=8, speed=6, color=color)
        
        # Update particle system
        self.particle_system.update()
        
        # Draw particles
        for particle in self.particle_system.particles:
            alpha = particle.get_alpha()
            if alpha > 0:
                color = (*particle.color, alpha)
                draw_glow_circle(canvas, (int(particle.x), int(particle.y)), 
                               particle.size, particle.color, thickness=-1, glow_size=2)
        
        # Store current landmarks for next frame
        self.prev_landmarks = landmarks.copy()
        
        return canvas
