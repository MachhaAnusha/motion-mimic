"""
Filter 2: Aura Burst
Particle art from movement with gesture controls
"""

import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional
from .base_filter import BaseFilter
from ..particles.particle_system import ParticleSystem
from ..gestures.gesture_detector import GestureDetector, GestureType


class AuraBurstFilter(BaseFilter):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__(width, height)
        
        # Particle system
        self.particle_system = ParticleSystem(max_particles=5000)
        
        # Gesture detector
        self.gesture_detector = GestureDetector()
        
        # Movement tracking
        self.previous_landmarks = None
        self.movement_threshold = 5.0
        self.burst_trigger_threshold = 20.0
        
        # Particle generation settings
        self.base_particle_density = 50
        self.movement_multiplier = 2.0
        
        # Hand tracking for firework effects
        self.hand_positions = []
        
    def apply(self, frame: np.ndarray, landmarks: List[Dict], 
              velocities: List[Dict], **kwargs) -> np.ndarray:
        """Apply aura burst filter"""
        canvas = self.create_black_canvas()
        
        # Get holistic results if available
        holistic_results = kwargs.get('holistic_results', None)
        
        if not landmarks or len(landmarks) < 33:
            self._draw_no_person_message(canvas)
            return canvas
            
        # Detect gestures
        gestures = {}
        if holistic_results:
            gestures = self.gesture_detector.detect_gestures(frame, holistic_results.pose_landmarks)
            
        # Process gestures
        self._process_gestures(gestures, landmarks)
        
        # Generate particles based on movement
        self._generate_movement_particles(landmarks, velocities)
        
        # Create hand firework effects
        if holistic_results and holistic_results.hand_landmarks:
            self._create_hand_fireworks(holistic_results.hand_landmarks, velocities)
            
        # Update and draw particles
        self.particle_system.update()
        self._draw_particles(canvas)
        
        # Draw subtle body outline
        self._draw_body_outline(canvas, landmarks)
        
        return canvas
        
    def _process_gestures(self, gestures: Dict, landmarks: List[Dict]):
        """Process gesture controls"""
        if gestures.get(GestureType.OPEN_PALM, False):
            self.particle_system.freeze()
        else:
            self.particle_system.unfreeze()
            
        if gestures.get(GestureType.CLOSED_FIST, False):
            self.particle_system.implode()
        else:
            self.particle_system.stop_implosion()
            
        if gestures.get(GestureType.POINT_UP, False):
            self.particle_system.change_theme()
            
        if gestures.get(GestureType.PINCH, False):
            self.particle_system.shrink()
        else:
            self.particle_system.stop_shrinking()
            
        if gestures.get(GestureType.TWO_HANDS_UP, False):
            # Full screen explosion
            self._create_fullscreen_explosion()
            
    def _generate_movement_particles(self, landmarks: List[Dict], velocities: List[Dict]):
        """Generate particles based on body movement"""
        if not velocities:
            return
            
        # Calculate overall movement
        total_movement = sum(v.get('magnitude', 0) for v in velocities)
        
        # Get body bounding box
        x_coords = [l['x'] for l in landmarks]
        y_coords = [l['y'] for l in landmarks]
        bounding_box = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
        
        # Generate particles based on movement intensity
        if total_movement > self.movement_threshold:
            # Calculate particle count based on movement
            movement_factor = min(3.0, total_movement / 50.0)
            particle_count = int(self.base_particle_density * movement_factor * self.intensity)
            
            # Create particles in silhouette
            self.particle_system.create_silhouette_particles(
                landmarks, bounding_box, particle_count
            )
            
            # Create burst effects for fast movement
            if total_movement > self.burst_trigger_threshold:
                # Find fastest moving point
                max_velocity_idx = max(range(len(velocities)), 
                                     key=lambda i: velocities[i].get('magnitude', 0))
                if max_velocity_idx < len(landmarks):
                    landmark = landmarks[max_velocity_idx]
                    x, y = landmark['x'] * self.width, landmark['y'] * self.height
                    self.particle_system.create_burst(x, y, 30, 15.0)
                    
    def _create_hand_fireworks(self, hand_landmarks, velocities: List[Dict]):
        """Create firework effects from hand movements"""
        for hand_idx, landmarks in enumerate(hand_landmarks):
            # Get wrist position
            wrist = landmarks.landmark[0]
            x, y = wrist.x * self.width, wrist.y * self.height
            
            # Store hand position
            self.hand_positions.append((x, y))
            if len(self.hand_positions) > 5:
                self.hand_positions.pop(0)
                
            # Check for fast hand movement
            if len(self.hand_positions) >= 2:
                prev_x, prev_y = self.hand_positions[-2]
                hand_velocity = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                
                if hand_velocity > 10:  # Fast hand movement
                    self.particle_system.create_burst(x, y, 20, 12.0)
                    
    def _create_fullscreen_explosion(self):
        """Create full screen particle explosion"""
        # Create multiple burst points across the screen
        for _ in range(10):
            x = np.random.uniform(100, self.width - 100)
            y = np.random.uniform(100, self.height - 100)
            self.particle_system.create_burst(x, y, 50, 20.0)
            
    def _draw_particles(self, canvas: np.ndarray):
        """Draw all particles"""
        for particle in self.particle_system.particles:
            if particle.is_alive():
                x, y = int(particle.x), int(particle.y)
                color = particle.color
                size = int(particle.get_size())
                alpha = int(particle.get_alpha())
                
                # Draw particle with glow effect
                if alpha > 0:
                    # Outer glow
                    glow_color = tuple(c // 3 for c in color)
                    cv2.circle(canvas, (x, y), size * 2, glow_color, -1)
                    # Main particle
                    cv2.circle(canvas, (x, y), size, color, -1)
                    # Bright center
                    cv2.circle(canvas, (x, y), max(1, size // 2), (255, 255, 255), -1)
                    
    def _draw_body_outline(self, canvas: np.ndarray, landmarks: List[Dict]):
        """Draw subtle body outline"""
        # Draw connections
        connections = [
            (11, 12), (11, 23), (12, 24), (23, 24),  # Torso
            (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
            (23, 25), (25, 27), (24, 26), (26, 28)   # Legs
        ]
        
        for connection in connections:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                pt1 = landmarks[connection[0]]
                pt2 = landmarks[connection[1]]
                
                x1, y1 = int(pt1['x'] * self.width), int(pt1['y'] * self.height)
                x2, y2 = int(pt2['x'] * self.width), int(pt2['y'] * self.height)
                
                # Draw subtle outline
                cv2.line(canvas, (x1, y1), (x2, y2), (50, 50, 50), 1)
                
    def _draw_no_person_message(self, canvas: np.ndarray):
        """Draw message when no person is detected"""
        text = "Step into frame"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1.0, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = self.height // 2
        
        cv2.putText(canvas, text, (text_x, text_y), font, 1.0, (100, 100, 255), 2)
        
    def reset(self):
        """Reset filter state"""
        self.particle_system.clear()
        self.hand_positions.clear()
        self.gesture_detector.reset()
        
    def set_intensity(self, intensity: float):
        """Set filter intensity"""
        super().set_intensity(intensity)
        self.base_particle_density = int(50 * intensity)
