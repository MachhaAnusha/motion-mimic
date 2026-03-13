import cv2
import numpy as np
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.drawing import draw_glow_line, draw_glow_circle

class NeonWireFilter:
    def __init__(self):
        self.name = "NEON WIRE"
        self.icon = "🔵"
        
        # Joint colors (33 MediaPipe landmarks)
        self.joint_colors = {
            0: '#FF0080',   # Nose (hot pink)
            1: '#FF00FF',   # Left eye (magenta)
            2: '#FF00FF',   # Right eye (magenta)
            3: '#FF00FF',   # Left ear (magenta)
            4: '#FF00FF',   # Right ear (magenta)
            5: '#FF6600',   # Left shoulder (neon orange)
            6: '#FF6600',   # Right shoulder (neon orange)
            7: '#FF3300',   # Left elbow (red-orange)
            8: '#FF3300',   # Right elbow (red-orange)
            9: '#FFFF00',   # Left wrist (electric yellow)
            10: '#FFFF00',  # Right wrist (electric yellow)
            11: '#00FF00',  # Left hip (lime green)
            12: '#00FF00',  # Right hip (lime green)
            13: '#FF00AA',  # Left knee (neon pink)
            14: '#FF00AA',  # Right knee (neon pink)
            15: '#AA00FF',  # Left ankle (violet)
            16: '#AA00FF',  # Right ankle (violet)
            17: '#00AAFF',  # Left foot (sky blue)
            18: '#00AAFF',  # Right foot (sky blue)
            19: '#FFFF00',  # Left pinky (electric yellow)
            20: '#FFFF00',  # Right pinky (electric yellow)
            21: '#FFFF00',  # Left index (electric yellow)
            22: '#FFFF00',  # Right index (electric yellow)
            23: '#FFFF00',  # Left thumb (electric yellow)
            24: '#FFFF00',  # Right thumb (electric yellow)
            25: '#FF00AA',  # Left heel (neon pink)
            26: '#FF00AA',  # Right heel (neon pink)
            27: '#FF00AA',  # Left foot index (neon pink)
            28: '#FF00AA',  # Right foot index (neon pink)
            29: '#FF00AA',  # Left big toe (neon pink)
            30: '#FF00AA',  # Right big toe (neon pink)
            31: '#FF00AA',  # Left small toe (neon pink)
            32: '#FF00AA',  # Right small toe (neon pink)
        }
        
        # Spine/mid points color
        self.spine_color = '#FF6600'  # Orange
        
        # Segment line colors
        self.segment_colors = {
            'head_to_neck': '#FF0080',      # Hot pink
            'neck_to_mid_torso': '#00FFFF',  # Cyan
            'mid_torso_to_hip_center': '#00FF99',  # Mint green
            'left_upper_arm': '#FF3300',     # Red-orange
            'left_forearm': '#FFFF00',       # Yellow
            'right_upper_arm': '#FF3300',    # Red-orange
            'right_forearm': '#FFFF00',      # Yellow
            'left_thigh': '#00FF00',        # Lime
            'left_shin': '#FF00AA',         # Pink
            'right_thigh': '#00FF00',       # Lime
            'right_shin': '#FF00AA',        # Pink
            'left_foot': '#AA00FF',         # Violet
            'right_foot': '#AA00FF',        # Violet
            'shoulder_bar': '#FF6600',      # Orange
            'hip_bar': '#FF6600',           # Orange
            'left_torso_side': '#00AAFF',   # Sky blue
            'right_torso_side': '#00AAFF',   # Sky blue
        }
        
        # MediaPipe pose connections (exact structure as specified)
        self.skeleton_connections = [
            # Neck
            ('neck', 'mid_shoulder', 'nose'),
            
            # Left arm
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            
            # Right arm
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            
            # Torso structure
            ('left_shoulder', 'right_shoulder'),  # TORSO_TOP
            ('left_shoulder', 'left_hip'),      # TORSO_L
            ('right_shoulder', 'right_hip'),     # TORSO_R
            ('left_hip', 'right_hip'),          # TORSO_BOT
            
            # Left leg
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('left_ankle', 'left_foot_index'),
            
            # Right leg
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle'),
            ('right_ankle', 'right_foot_index'),
        ]
        
        # Landmark name to index mapping
        self.landmark_names = {
            'nose': 0,
            'left_eye': 1, 'right_eye': 2,
            'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
            'left_foot_index': 29, 'right_foot_index': 30,
            'left_heel': 25, 'right_heel': 26,  # Use knee as heel proxy
        }
    
    def hex_to_bgr(self, hex_color):
        """Convert hex color to BGR tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))
    
    def draw_glowing_joint(self, canvas, point, color_hex, size=4):
        """Draw a sharp glowing joint with subtle glow"""
        color = self.hex_to_bgr(color_hex)
        
        # Step 1: Draw joint glow on separate layer
        glow_layer = np.zeros_like(canvas)
        cv2.circle(glow_layer, point, 5, color, -1)  # 5px radius for glow
        
        # Step 2: Apply subtle blur to glow layer
        glow_layer = cv2.GaussianBlur(glow_layer, (7, 7), 2)
        
        # Step 3: Blend glow with canvas
        cv2.addWeighted(canvas, 1.0, glow_layer, 0.55, 0, canvas)
        
        # Step 4: Draw sharp core dot on top
        cv2.circle(canvas, point, size, color, -1)  # 4px core dot
    
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
    
    def draw_head_circle(self, canvas, points):
        """Draw single head circle instead of scattered face landmarks"""
        if len(points) > 4:  # Need nose, left ear, right ear
            nose_point = points[0]  # Nose landmark
            left_ear_point = points[3]  # Left ear
            right_ear_point = points[4]  # Right ear
            
            # Calculate head radius based on ear distance
            ear_distance = math.sqrt((left_ear_point[0] - right_ear_point[0])**2 + 
                                 (left_ear_point[1] - right_ear_point[1])**2)
            head_radius = int(ear_distance * 1.2)
            
            # Draw head circle with hot pink color and glow
            self.draw_glowing_circle(canvas, nose_point, '#FF0080', head_radius, stroke_thickness=2)
            
            # Draw small nose dot
            self.draw_glowing_joint(canvas, nose_point, '#FF0080', size=6)
    
    def draw_glowing_circle(self, canvas, center, color_hex, radius, stroke_thickness=2):
        """Draw a glowing circle with stroke"""
        color = self.hex_to_bgr(color_hex)
        
        # Draw glow layer
        glow_layer = np.zeros_like(canvas)
        cv2.circle(glow_layer, center, radius + 2, color, stroke_thickness + 1)
        glow_layer = cv2.GaussianBlur(glow_layer, (7, 7), 2)
        cv2.addWeighted(canvas, 1.0, glow_layer, 0.55, 0, canvas)
        
        # Draw core circle
        cv2.circle(canvas, center, radius, color, stroke_thickness)
    
    def get_landmark_point(self, landmark_name, points, landmarks):
        """Get landmark point with visibility check"""
        if landmark_name in self.landmark_names:
            idx = self.landmark_names[landmark_name]
            if idx < len(points) and idx < len(landmarks):
                if landmarks[idx].get('visibility', 0) > 0.5:
                    return points[idx]
        return None
    
    def get_midpoint(self, pt1, pt2):
        """Get midpoint between two points"""
        if pt1 and pt2:
            return ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)
        return None
    
    def apply(self, frame, landmarks, width, height):
        """Apply neon wire filter to frame"""
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        if not landmarks:
            return canvas
        
        # Convert normalized landmarks to pixel coordinates
        points = []
        for landmark in landmarks:
            x = int(landmark['x'] * width)
            y = int(landmark['y'] * height)
            points.append((x, y))
        
        # Get landmark points with visibility check
        def get_point(name):
            return self.get_landmark_point(name, points, landmarks)
        
        # === HEAD ===
        nose_point = get_point('nose')
        if nose_point:
            # Draw head circle (25px fixed size)
            self.draw_glowing_circle(canvas, nose_point, '#FF0000', 25, stroke_thickness=2)
            # Draw small filled dot at center
            cv2.circle(canvas, nose_point, 3, self.hex_to_bgr('#FF0000'), -1)
        
        # === KEY POINTS ===
        left_shoulder = get_point('left_shoulder')
        right_shoulder = get_point('right_shoulder')
        left_hip = get_point('left_hip')
        right_hip = get_point('right_hip')
        left_elbow = get_point('left_elbow')
        right_elbow = get_point('right_elbow')
        left_wrist = get_point('left_wrist')
        right_wrist = get_point('right_wrist')
        left_knee = get_point('left_knee')
        right_knee = get_point('right_knee')
        left_ankle = get_point('left_ankle')
        right_ankle = get_point('right_ankle')
        left_foot = get_point('left_foot_index')
        right_foot = get_point('right_foot_index')
        
        # Calculate midpoints
        mid_shoulder = self.get_midpoint(left_shoulder, right_shoulder)
        mid_hip = self.get_midpoint(left_hip, right_hip)
        
        # === NECK ===
        if nose_point and mid_shoulder:
            self.draw_glowing_line(canvas, nose_point, mid_shoulder, '#FF0000', thickness=3)
        
        # === TORSO PENTAGON ===
        if all([mid_shoulder, left_shoulder, right_shoulder, left_hip, right_hip, mid_hip]):
            # Torso outline (pentagon shape)
            torso_lines = [
                (mid_shoulder, left_shoulder),      # Top-left
                (mid_shoulder, right_shoulder),     # Top-right
                (left_shoulder, left_hip),          # Left side
                (right_shoulder, right_hip),        # Right side
                (left_hip, mid_hip),                # Bottom-left
                (right_hip, mid_hip),               # Bottom-right
            ]
            
            for pt1, pt2 in torso_lines:
                if pt1 and pt2:
                    self.draw_glowing_line(canvas, pt1, pt2, '#0000FF', thickness=3)
            
            # Spine line (thinner, through center)
            if mid_shoulder and mid_hip:
                self.draw_glowing_line(canvas, mid_shoulder, mid_hip, '#00FFFF', thickness=1)
        
        # === CROSSBARS ===
        if left_shoulder and right_shoulder:
            self.draw_glowing_line(canvas, left_shoulder, right_shoulder, '#FF00FF', thickness=2)
        if left_hip and right_hip:
            self.draw_glowing_line(canvas, left_hip, right_hip, '#FFFF00', thickness=2)
        
        # === ARMS ===
        if left_shoulder and left_elbow:
            self.draw_glowing_line(canvas, left_shoulder, left_elbow, '#FF0000', thickness=3)
        if left_elbow and left_wrist:
            self.draw_glowing_line(canvas, left_elbow, left_wrist, '#FF0000', thickness=3)
            
        if right_shoulder and right_elbow:
            self.draw_glowing_line(canvas, right_shoulder, right_elbow, '#FF0000', thickness=3)
        if right_elbow and right_wrist:
            self.draw_glowing_line(canvas, right_elbow, right_wrist, '#FF0000', thickness=3)
        
        # === LEGS ===
        if left_hip and left_knee:
            self.draw_glowing_line(canvas, left_hip, left_knee, '#00FF00', thickness=3)
        if left_knee and left_ankle:
            self.draw_glowing_line(canvas, left_knee, left_ankle, '#00FF00', thickness=3)
            
        if right_hip and right_knee:
            self.draw_glowing_line(canvas, right_hip, right_knee, '#00FF00', thickness=3)
        if right_knee and right_ankle:
            self.draw_glowing_line(canvas, right_knee, right_ankle, '#00FF00', thickness=3)
        
        # === FEET ===
        if left_ankle and left_foot:
            self.draw_glowing_line(canvas, left_ankle, left_foot, '#FF0000', thickness=3)
        if right_ankle and right_foot:
            self.draw_glowing_line(canvas, right_ankle, right_foot, '#FF0000', thickness=3)
        
        # === JOINT DOTS ===
        joint_configs = [
            (left_shoulder, '#FF00FF', 7),    # Shoulders - magenta, 7px
            (right_shoulder, '#FF00FF', 7),
            (left_hip, '#FFFF00', 7),        # Hips - yellow, 7px
            (right_hip, '#FFFF00', 7),
            (left_knee, '#00FF00', 6),        # Knees - green, 6px
            (right_knee, '#00FF00', 6),
            (left_elbow, '#FF0000', 6),        # Elbows - red, 6px
            (right_elbow, '#FF0000', 6),
            (left_wrist, '#FF0000', 5),        # Wrists - red, 5px
            (right_wrist, '#FF0000', 5),
            (left_ankle, '#FF0000', 5),        # Ankles - red, 5px
            (right_ankle, '#FF0000', 5),
            (left_foot, '#FF0000', 5),         # Feet - red, 5px
            (right_foot, '#FF0000', 5),
        ]
        
        for point, color, radius in joint_configs:
            if point:
                self.draw_glowing_joint(canvas, point, color, size=radius)
        
        return canvas
