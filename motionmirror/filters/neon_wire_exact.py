import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.drawing import hex_to_bgr

class NeonWireExactFilter:
    def __init__(self):
        self.name = "NEON WIRE"
        self.icon = "🔵"
        
        # Initialize MediaPipe with maximum accuracy
        import mediapipe as mp
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,          # HEAVY model for maximum accuracy
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    
    def hex_to_bgr(self, hex_color):
        """Convert hex color to BGR tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))
    
    def draw_glowing_line(self, canvas, pt1, pt2, color_hex, thickness=3):
        """Draw a sharp glowing line with subtle glow"""
        color = self.hex_to_bgr(color_hex)
        
        # Step 1: Draw line glow on separate layer
        glow_layer = np.zeros_like(canvas)
        cv2.line(glow_layer, pt1, pt2, color, thickness + 2)  # Slightly thicker for glow
        
        # Step 2: Apply subtle blur to glow layer
        glow_layer = cv2.GaussianBlur(glow_layer, (9, 9), 3)  # 9x9 kernel, sigma=3
        
        # Step 3: Blend glow with canvas
        cv2.addWeighted(canvas, 1.0, glow_layer, 0.5, 0, canvas)
        
        # Step 4: Draw sharp core line on top
        cv2.line(canvas, pt1, pt2, color, thickness)
    
    def draw_glowing_joint(self, canvas, point, color_hex, radius=5):
        """Draw a glowing joint with subtle glow"""
        color = self.hex_to_bgr(color_hex)
        
        # Step 1: Draw joint glow on separate layer
        glow_layer = np.zeros_like(canvas)
        cv2.circle(glow_layer, point, radius + 3, color, -1)  # Glow layer
        
        # Step 2: Apply subtle blur to glow layer
        glow_layer = cv2.GaussianBlur(glow_layer, (9, 9), 3)
        
        # Step 3: Blend glow with canvas
        cv2.addWeighted(canvas, 1.0, glow_layer, 0.5, 0, canvas)
        
        # Step 4: Draw sharp core dot on top
        cv2.circle(canvas, point, radius, color, -1)
    
    def get_landmark(self, landmark_idx, landmarks):
        """Get landmark with visibility check"""
        if landmark_idx < len(landmarks):
            lm = landmarks[landmark_idx]
            if lm.visibility > 0.6 and lm.presence > 0.6:  # Stricter visibility check
                return lm
        return None
    
    def in_bounds(self, pt, w, h):
        """Check if point is within frame bounds"""
        return 0 < pt[0] < w and 0 < pt[1] < h
    
    def apply(self, frame, landmarks, width, height):
        """Apply exact NEON WIRE filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if not landmarks:
            return canvas
        
        # Flip frame horizontally for mirror mode
        frame = cv2.flip(frame, 1)
        
        # Process with MediaPipe for accurate landmarks
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        if not results.pose_landmarks:
            return canvas
        
        # Convert MediaPipe landmarks to our format
        processed_landmarks = []
        for lm in results.pose_landmarks.landmark:
            processed_landmarks.append({
                'x': lm.x,
                'y': lm.y,
                'z': lm.z,
                'visibility': lm.visibility,
                'presence': lm.presence
            })
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # === EXACT LANDMARK INDICES ===
        nose = self.get_landmark(0, processed_landmarks)
        left_shoulder = self.get_landmark(11, processed_landmarks)
        right_shoulder = self.get_landmark(12, processed_landmarks)
        left_elbow = self.get_landmark(13, processed_landmarks)
        right_elbow = self.get_landmark(14, processed_landmarks)
        left_wrist = self.get_landmark(15, processed_landmarks)
        right_wrist = self.get_landmark(16, processed_landmarks)
        left_hip = self.get_landmark(23, processed_landmarks)
        right_hip = self.get_landmark(24, processed_landmarks)
        left_knee = self.get_landmark(25, processed_landmarks)
        right_knee = self.get_landmark(26, processed_landmarks)
        left_ankle = self.get_landmark(27, processed_landmarks)
        right_ankle = self.get_landmark(28, processed_landmarks)
        left_foot = self.get_landmark(31, processed_landmarks)
        right_foot = self.get_landmark(32, processed_landmarks)
        
        # === HELPER FUNCTIONS ===
        def to_pixel(lm):
            if lm and self.in_bounds((int(lm.x * w), int(lm.y * h)), w, h):
                return (int(lm.x * w), int(lm.y * h))
            return None
        
        def midpoint(lm1, lm2):
            if lm1 and lm2:
                p1 = to_pixel(lm1)
                p2 = to_pixel(lm2)
                if p1 and p2:
                    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            return None
        
        # Convert landmarks to pixel coordinates
        nose_pt = to_pixel(nose)
        left_shoulder_pt = to_pixel(left_shoulder)
        right_shoulder_pt = to_pixel(right_shoulder)
        left_elbow_pt = to_pixel(left_elbow)
        right_elbow_pt = to_pixel(right_elbow)
        left_wrist_pt = to_pixel(left_wrist)
        right_wrist_pt = to_pixel(right_wrist)
        left_hip_pt = to_pixel(left_hip)
        right_hip_pt = to_pixel(right_hip)
        left_knee_pt = to_pixel(left_knee)
        right_knee_pt = to_pixel(right_knee)
        left_ankle_pt = to_pixel(left_ankle)
        right_ankle_pt = to_pixel(right_ankle)
        left_foot_pt = to_pixel(left_foot)
        right_foot_pt = to_pixel(right_foot)
        
        # Calculate midpoints
        mid_shoulder_pt = midpoint(left_shoulder_pt, right_shoulder_pt)
        mid_hip_pt = midpoint(left_hip_pt, right_hip_pt)
        
        # === GLOW LAYER ===
        glow = np.zeros_like(canvas)
        
        # === STEP 1: DRAW ALL STRUCTURE ON GLOW LAYER ===
        
        # HEAD circle
        if nose_pt:
            cv2.circle(glow, nose_pt, 22, self.hex_to_bgr('#FF0000'), 2)  # Red head
        
        # Neck line
        if nose_pt and mid_shoulder_pt:
            cv2.line(glow, nose_pt, mid_shoulder_pt, self.hex_to_bgr('#FF0000'), 5)  # Red neck
        
        # Torso diamond (NO FILL)
        if all([mid_shoulder_pt, left_shoulder_pt, right_shoulder_pt, left_hip_pt, right_hip_pt, mid_hip_pt]):
            # Top lines
            cv2.line(glow, mid_shoulder_pt, left_shoulder_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue top-left
            cv2.line(glow, mid_shoulder_pt, right_shoulder_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue top-right
            cv2.line(glow, left_shoulder_pt, left_hip_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue left side
            cv2.line(glow, right_shoulder_pt, right_hip_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue right side
            cv2.line(glow, left_hip_pt, right_hip_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue bottom
            cv2.line(glow, left_hip_pt, mid_hip_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue to center
            cv2.line(glow, right_hip_pt, mid_hip_pt, self.hex_to_bgr('#0000FF'), 5)  # Blue to center
            
            # Spine line
            if mid_shoulder_pt and mid_hip_pt:
                cv2.line(glow, mid_shoulder_pt, mid_hip_pt, self.hex_to_bgr('#00FFFF'), 3)  # Cyan spine
        
        # Shoulders crossbar
        if left_shoulder_pt and right_shoulder_pt:
            cv2.line(glow, left_shoulder_pt, right_shoulder_pt, self.hex_to_bgr('#FF00FF'), 4)  # Magenta shoulders
        
        # Hips crossbar
        if left_hip_pt and right_hip_pt:
            cv2.line(glow, left_hip_pt, right_hip_pt, self.hex_to_bgr('#FFFF00'), 4)  # Yellow hips
        
        # Arms
        if left_shoulder_pt and left_elbow_pt:
            cv2.line(glow, left_shoulder_pt, left_elbow_pt, self.hex_to_bgr('#FF4400'), 5)  # Red-orange left arm
        if left_elbow_pt and left_wrist_pt:
            cv2.line(glow, left_elbow_pt, left_wrist_pt, self.hex_to_bgr('#FF0000'), 5)  # Red left forearm
        if right_shoulder_pt and right_elbow_pt:
            cv2.line(glow, right_shoulder_pt, right_elbow_pt, self.hex_to_bgr('#FF4400'), 5)  # Red-orange right arm
        if right_elbow_pt and right_wrist_pt:
            cv2.line(glow, right_elbow_pt, right_wrist_pt, self.hex_to_bgr('#FF0000'), 5)  # Red right forearm
        
        # Legs
        if left_hip_pt and left_knee_pt:
            cv2.line(glow, left_hip_pt, left_knee_pt, self.hex_to_bgr('#00FF00'), 5)  # Lime left thigh
        if left_knee_pt and left_ankle_pt:
            cv2.line(glow, left_knee_pt, left_ankle_pt, self.hex_to_bgr('#00FF00'), 5)  # Lime left shin
        if left_ankle_pt and left_foot_pt:
            cv2.line(glow, left_ankle_pt, left_foot_pt, self.hex_to_bgr('#FF0000'), 4)  # Red left foot
        if right_hip_pt and right_knee_pt:
            cv2.line(glow, right_hip_pt, right_knee_pt, self.hex_to_bgr('#00FF00'), 5)  # Lime right thigh
        if right_knee_pt and right_ankle_pt:
            cv2.line(glow, right_knee_pt, right_ankle_pt, self.hex_to_bgr('#00FF00'), 5)  # Lime right shin
        if right_ankle_pt and right_foot_pt:
            cv2.line(glow, right_ankle_pt, right_foot_pt, self.hex_to_bgr('#FF0000'), 4)  # Red right foot
        
        # === STEP 2: APPLY GAUSSIAN BLUR TO GLOW ===
        glow_blurred = cv2.GaussianBlur(glow, (9, 9), 3)
        
        # === STEP 3: BLEND GLOW WITH CANVAS ===
        canvas = cv2.addWeighted(canvas, 1.0, glow_blurred, 0.6, 0)
        
        # === STEP 4: DRAW SHARP CORE ELEMENTS ON TOP ===
        
        # Head circle (sharp)
        if nose_pt:
            cv2.circle(canvas, nose_pt, 22, self.hex_to_bgr('#FF0000'), 2)  # Red head with 2px stroke
            cv2.circle(canvas, nose_pt, 3, self.hex_to_bgr('#FF0000'), -1)  # Center dot
        
        # Neck line (sharp)
        if nose_pt and mid_shoulder_pt:
            cv2.line(canvas, nose_pt, mid_shoulder_pt, self.hex_to_bgr('#FF0000'), 3)  # Red neck
        
        # Torso lines (sharp)
        if all([mid_shoulder_pt, left_shoulder_pt, right_shoulder_pt, left_hip_pt, right_hip_pt, mid_hip_pt]):
            cv2.line(canvas, mid_shoulder_pt, left_shoulder_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue top-left
            cv2.line(canvas, mid_shoulder_pt, right_shoulder_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue top-right
            cv2.line(canvas, left_shoulder_pt, left_hip_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue left side
            cv2.line(canvas, right_shoulder_pt, right_hip_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue right side
            cv2.line(canvas, left_hip_pt, right_hip_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue bottom
            cv2.line(canvas, left_hip_pt, mid_hip_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue to center
            cv2.line(canvas, right_hip_pt, mid_hip_pt, self.hex_to_bgr('#0000FF'), 3)  # Blue to center
            
            # Spine line (sharp, thinner)
            if mid_shoulder_pt and mid_hip_pt:
                cv2.line(canvas, mid_shoulder_pt, mid_hip_pt, self.hex_to_bgr('#00FFFF'), 1)  # Cyan spine
        
        # Shoulders crossbar (sharp)
        if left_shoulder_pt and right_shoulder_pt:
            cv2.line(canvas, left_shoulder_pt, right_shoulder_pt, self.hex_to_bgr('#FF00FF'), 2)  # Magenta shoulders
        
        # Hips crossbar (sharp)
        if left_hip_pt and right_hip_pt:
            cv2.line(canvas, left_hip_pt, right_hip_pt, self.hex_to_bgr('#FFFF00'), 2)  # Yellow hips
        
        # Arms (sharp)
        if left_shoulder_pt and left_elbow_pt:
            cv2.line(canvas, left_shoulder_pt, left_elbow_pt, self.hex_to_bgr('#FF4400'), 3)  # Red-orange left arm
        if left_elbow_pt and left_wrist_pt:
            cv2.line(canvas, left_elbow_pt, left_wrist_pt, self.hex_to_bgr('#FF0000'), 3)  # Red left forearm
        if right_shoulder_pt and right_elbow_pt:
            cv2.line(canvas, right_shoulder_pt, right_elbow_pt, self.hex_to_bgr('#FF4400'), 3)  # Red-orange right arm
        if right_elbow_pt and right_wrist_pt:
            cv2.line(canvas, right_elbow_pt, right_wrist_pt, self.hex_to_bgr('#FF0000'), 3)  # Red right forearm
        
        # Legs (sharp)
        if left_hip_pt and left_knee_pt:
            cv2.line(canvas, left_hip_pt, left_knee_pt, self.hex_to_bgr('#00FF00'), 3)  # Lime left thigh
        if left_knee_pt and left_ankle_pt:
            cv2.line(canvas, left_knee_pt, left_ankle_pt, self.hex_to_bgr('#00FF00'), 3)  # Lime left shin
        if left_ankle_pt and left_foot_pt:
            cv2.line(canvas, left_ankle_pt, left_foot_pt, self.hex_to_bgr('#FF0000'), 3)  # Red left foot
        if right_hip_pt and right_knee_pt:
            cv2.line(canvas, right_hip_pt, right_knee_pt, self.hex_to_bgr('#00FF00'), 3)  # Lime right thigh
        if right_knee_pt and right_ankle_pt:
            cv2.line(canvas, right_knee_pt, right_ankle_pt, self.hex_to_bgr('#00FF00'), 3)  # Lime right shin
        if right_ankle_pt and right_foot_pt:
            cv2.line(canvas, right_ankle_pt, right_foot_pt, self.hex_to_bgr('#FF0000'), 3)  # Red right foot
        
        # === STEP 5: DRAW JOINT DOTS (SHARP, NO BLUR) ===
        
        # Joint configurations with exact colors and sizes
        joint_configs = [
            (mid_shoulder_pt, '#FF00FF', 7),    # Shoulders - magenta, 7px
            (mid_hip_pt, '#FFFF00', 7),        # Hips - yellow, 7px
            (left_knee_pt, '#00FF00', 6),        # Knees - green, 6px
            (right_knee_pt, '#00FF00', 6),
            (left_elbow_pt, '#FF4400', 6),      # Elbows - red-orange, 6px
            (right_elbow_pt, '#FF4400', 6),
            (left_wrist_pt, '#FF0000', 5),        # Wrists - red, 5px
            (right_wrist_pt, '#FF0000', 5),
            (left_ankle_pt, '#FF0000', 5),        # Ankles - red, 5px
            (left_foot_pt, '#FF0000', 5),         # Feet - red, 5px
            (right_foot_pt, '#FF0000', 5),
        ]
        
        # Draw all joint dots (sharp, no blur)
        for point, color, radius in joint_configs:
            if point:
                cv2.circle(canvas, point, radius, self.hex_to_bgr(color), -1)
        
        return canvas
    
    def close(self):
        """Clean up MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
