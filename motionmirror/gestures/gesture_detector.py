"""
Gesture detection using MediaPipe Hands
"""

import mediapipe as mp
import numpy as np
import cv2
import time
from typing import List, Dict, Optional, Tuple
from enum import Enum


class GestureType(Enum):
    OPEN_PALM = "open_palm"
    CLOSED_FIST = "closed_fist"
    POINT_UP = "point_up"
    PINCH = "pinch"
    TWO_HANDS_UP = "two_hands_up"


class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.gesture_timers = {}
        self.last_gesture_time = {}
        self.gesture_threshold = 1.0  # seconds for sustained gestures
        
    def detect_gestures(self, image: np.ndarray, pose_landmarks) -> Dict[GestureType, bool]:
        """Detect gestures from image and pose landmarks"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_image)
        
        gestures = {gesture: False for gesture in GestureType}
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks
            
            # Detect individual hand gestures
            for i, landmarks in enumerate(hand_landmarks):
                hand_gestures = self._analyze_hand(landmarks)
                
                for gesture, detected in hand_gestures.items():
                    if detected:
                        current_time = time.time()
                        
                        # Check for sustained gestures
                        if gesture in [GestureType.OPEN_PALM, GestureType.CLOSED_FIST]:
                            if gesture not in self.gesture_timers:
                                self.gesture_timers[gesture] = current_time
                            elif current_time - self.gesture_timers[gesture] >= self.gesture_threshold:
                                gestures[gesture] = True
                                self.gesture_timers[gesture] = None  # Reset after trigger
                        else:
                            # Immediate gestures
                            if gesture not in self.last_gesture_time or \
                               current_time - self.last_gesture_time[gesture] > 0.5:
                                gestures[gesture] = True
                                self.last_gesture_time[gesture] = current_time
                                
            # Check for two hands up
            if len(hand_landmarks) == 2:
                gestures[GestureType.TWO_HANDS_UP] = self._check_two_hands_up(hand_landmarks, pose_landmarks)
                
        # Clean up old timers
        self._cleanup_timers()
        
        return gestures
        
    def _analyze_hand(self, landmarks) -> Dict[GestureType, bool]:
        """Analyze individual hand for gestures"""
        gestures = {gesture: False for gesture in GestureType}
        
        # Get key landmark positions
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]
        ring_tip = landmarks.landmark[16]
        ring_pip = landmarks.landmark[14]
        pinky_tip = landmarks.landmark[20]
        pinky_pip = landmarks.landmark[18]
        wrist = landmarks.landmark[0]
        
        # Check if fingers are extended
        thumb_extended = thumb_tip.y < thumb_ip.y
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        ring_extended = ring_tip.y < ring_pip.y
        pinky_extended = pinky_tip.y < pinky_pip.y
        
        extended_count = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
        
        # Open palm (all fingers extended)
        if extended_count >= 4:
            gestures[GestureType.OPEN_PALM] = True
            
        # Closed fist (no fingers extended)
        elif extended_count <= 1:
            gestures[GestureType.CLOSED_FIST] = True
            
        # Point up (only index finger extended)
        elif index_extended and extended_count == 1:
            gestures[GestureType.POINT_UP] = True
            
        # Pinch (thumb and index close together)
        thumb_index_dist = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        if thumb_index_dist < 0.05:
            gestures[GestureType.PINCH] = True
            
        return gestures
        
    def _check_two_hands_up(self, hand_landmarks, pose_landmarks) -> bool:
        """Check if both hands are raised above head"""
        if not pose_landmarks or len(pose_landmarks.landmark) < 33:
            return False
            
        # Get head position
        head_y = pose_landmarks.landmark[0].y  # Nose
        
        # Check both hands
        hands_up = 0
        for landmarks in hand_landmarks:
            wrist_y = landmarks.landmark[0].y
            if wrist_y < head_y:  # Hand is above head
                hands_up += 1
                
        return hands_up == 2
        
    def _cleanup_timers(self):
        """Clean up old gesture timers"""
        current_time = time.time()
        expired_timers = []
        
        for gesture, start_time in self.gesture_timers.items():
            if start_time is not None and current_time - start_time > self.gesture_threshold * 2:
                expired_timers.append(gesture)
                
        for gesture in expired_timers:
            del self.gesture_timers[gesture]
            
    def reset(self):
        """Reset gesture detection state"""
        self.gesture_timers.clear()
        self.last_gesture_time.clear()
