import cv2
import mediapipe as mp
import numpy as np
import math
import time
from typing import List, Dict, Tuple, Optional

class PoseDetector:
    def __init__(self):
        try:
            # Use holistic for combined pose + hands + face detection
            self.mp_holistic = mp.solutions.holistic
            self.mp_drawing = mp.solutions.drawing_utils
            self.holistic = self.mp_holistic.Holistic(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                refine_face_landmarks=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.use_mediapipe = True
            
            # Store previous landmarks for velocity calculation
            self.previous_landmarks = None
            self.previous_time = None
            
        except AttributeError:
            self.use_mediapipe = False
            print("MediaPipe solutions not available, using fallback mode")
        
    def detect(self, frame):
        """Detect pose landmarks in frame"""
        if self.use_mediapipe:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(rgb_frame)
            
            landmarks = []
            if results.pose_landmarks:
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
            
            # Calculate velocities
            velocities = self._calculate_velocities(landmarks)
            
            # Store current landmarks for next frame
            self.previous_landmarks = landmarks
            self.previous_time = time.time()
            
            return landmarks, results.pose_landmarks, velocities, results
        else:
            return [], None, [], None
    
    def _calculate_velocities(self, landmarks: List[Dict]) -> List[Dict]:
        """Calculate velocity for each landmark"""
        velocities = []
        
        if not self.previous_landmarks or not landmarks:
            return velocities
            
        for i, landmark in enumerate(landmarks):
            if i < len(self.previous_landmarks):
                prev = self.previous_landmarks[i]
                # Calculate pixel velocity
                dx = (landmark['x'] - prev['x']) * 1280  # Scale to frame width
                dy = (landmark['y'] - prev['y']) * 720   # Scale to frame height
                velocity = math.sqrt(dx*dx + dy*dy)
                
                velocities.append({
                    'x': dx,
                    'y': dy,
                    'magnitude': velocity
                })
            else:
                velocities.append({'x': 0, 'y': 0, 'magnitude': 0})
                
        return velocities
    
    def get_bounding_box(self, landmarks: List[Dict]) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding box of pose landmarks"""
        if not landmarks:
            return None
            
        x_coords = [l['x'] for l in landmarks]
        y_coords = [l['y'] for l in landmarks]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def detect_punch(self, landmarks: List[Dict], velocities: List[Dict]) -> Dict[str, bool]:
        """Detect punch and kick gestures"""
        gestures = {'punch_left': False, 'punch_right': False, 'kick_left': False, 'kick_right': False}
        
        if not landmarks or not velocities or len(landmarks) < 33:
            return gestures
            
        # Check wrist velocities for punches
        left_wrist_idx = 15
        right_wrist_idx = 16
        left_ankle_idx = 27
        right_ankle_idx = 28
        
        # Punch detection (high forward velocity)
        if left_wrist_idx < len(velocities):
            if velocities[left_wrist_idx]['magnitude'] > 15:
                gestures['punch_left'] = True
                
        if right_wrist_idx < len(velocities):
            if velocities[right_wrist_idx]['magnitude'] > 15:
                gestures['punch_right'] = True
                
        # Kick detection
        if left_ankle_idx < len(velocities):
            if velocities[left_ankle_idx]['magnitude'] > 12:
                gestures['kick_left'] = True
                
        if right_ankle_idx < len(velocities):
            if velocities[right_ankle_idx]['magnitude'] > 12:
                gestures['kick_right'] = True
                
        return gestures
    
    def get_connections(self):
        """Get pose connections for drawing skeleton"""
        if self.use_mediapipe:
            return self.mp_holistic.POSE_CONNECTIONS
        else:
            return []
    
    def close(self):
        """Clean up resources"""
        if self.use_mediapipe:
            self.holistic.close()
