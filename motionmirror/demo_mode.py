import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import time
import math

# Import the exact NEON WIRE filter
from filters.neon_wire_exact import NeonWireExactFilter

class DemoMotionMirror(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOTION MIRROR - Enhanced NEON WIRE Demo")
        self.setGeometry(100, 100, 1280, 720)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Create label for displaying video
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            background-color: black; 
            color: white; 
            font-size: 20px; 
            font-weight: bold;
            border: 2px solid #333;
        """)
        self.video_label.setText("MOTION MIRROR - Enhanced NEON WIRE\n\nGenerating full-spectrum neon skeleton...")
        layout.addWidget(self.video_label)
        
        # Initialize the enhanced Neon Wire filter
        self.neon_filter = NeonWireFilter()
        
        # Animation setup
        self.frame_count = 0
        self.time_start = time.time()
        
        # Timer for animation update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_demo_frame)
        self.timer.start(33)  # ~30 FPS
        
        print("MOTION MIRROR Enhanced NEON WIRE Demo started - Showing full-spectrum neon skeleton")
    
    def create_demo_landmarks(self, width, height):
        """Create realistic demo pose landmarks matching MediaPipe 33-point structure"""
        t = time.time() - self.time_start
        
        # Create 33 landmarks with realistic human pose
        landmarks = []
        
        # Face/head (0-10)
        head_x = 0.5 + math.sin(t * 0.5) * 0.05
        head_y = 0.15
        
        # Nose (0)
        landmarks.append({'x': head_x, 'y': head_y, 'z': 0.0, 'visibility': 1.0})
        
        # Eyes (1-2)
        landmarks.append({'x': head_x - 0.02, 'y': head_y + 0.02, 'z': 0.0, 'visibility': 1.0})
        landmarks.append({'x': head_x + 0.02, 'y': head_y + 0.02, 'z': 0.0, 'visibility': 1.0})
        
        # Ears (3-4)
        landmarks.append({'x': head_x - 0.04, 'y': head_y + 0.01, 'z': 0.0, 'visibility': 1.0})
        landmarks.append({'x': head_x + 0.04, 'y': head_y + 0.01, 'z': 0.0, 'visibility': 1.0})
        
        # Mouth/face points (5-10) - simplified
        for i in range(6):
            landmarks.append({'x': head_x + (i-2.5) * 0.015, 'y': head_y + 0.05, 'z': 0.0, 'visibility': 1.0})
        
        # Shoulders (5-6) - using indices 11-12 in actual MediaPipe
        shoulder_y = 0.35
        left_shoulder_x = 0.35 + math.sin(t * 0.8) * 0.05
        right_shoulder_x = 0.65 + math.cos(t * 0.8) * 0.05
        
        landmarks.insert(11, {'x': left_shoulder_x, 'y': shoulder_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(12, {'x': right_shoulder_x, 'y': shoulder_y, 'z': 0.0, 'visibility': 1.0})
        
        # Elbows (7-8) - indices 13-14
        left_elbow_x = left_shoulder_x + math.sin(t * 1.2) * 0.15
        left_elbow_y = shoulder_y + 0.15
        right_elbow_x = right_shoulder_x + math.cos(t * 1.2) * 0.15
        right_elbow_y = shoulder_y + 0.15
        
        landmarks.insert(13, {'x': left_elbow_x, 'y': left_elbow_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(14, {'x': right_elbow_x, 'y': right_elbow_y, 'z': 0.0, 'visibility': 1.0})
        
        # Wrists (9-10) - indices 15-16
        left_wrist_x = left_elbow_x + math.sin(t * 2) * 0.12
        left_wrist_y = left_elbow_y + 0.12
        right_wrist_x = right_elbow_x + math.cos(t * 2) * 0.12
        right_wrist_y = right_elbow_y + 0.12
        
        landmarks.insert(15, {'x': left_wrist_x, 'y': left_wrist_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(16, {'x': right_wrist_x, 'y': right_wrist_y, 'z': 0.0, 'visibility': 1.0})
        
        # Hips (11-12) - indices 23-24
        hip_y = 0.6
        left_hip_x = 0.4
        right_hip_x = 0.6
        
        landmarks.insert(23, {'x': left_hip_x, 'y': hip_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(24, {'x': right_hip_x, 'y': hip_y, 'z': 0.0, 'visibility': 1.0})
        
        # Knees (13-14) - indices 25-26
        left_knee_x = left_hip_x + math.sin(t * 0.6) * 0.08
        left_knee_y = hip_y + 0.15
        right_knee_x = right_hip_x + math.cos(t * 0.6) * 0.08
        right_knee_y = hip_y + 0.15
        
        landmarks.insert(25, {'x': left_knee_x, 'y': left_knee_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(26, {'x': right_knee_x, 'y': right_knee_y, 'z': 0.0, 'visibility': 1.0})
        
        # Ankles (15-16) - indices 27-28
        left_ankle_x = left_knee_x + math.sin(t * 0.8) * 0.06
        left_ankle_y = left_knee_y + 0.15
        right_ankle_x = right_knee_x + math.cos(t * 0.8) * 0.06
        right_ankle_y = right_knee_y + 0.15
        
        landmarks.insert(27, {'x': left_ankle_x, 'y': left_ankle_y, 'z': 0.0, 'visibility': 1.0})
        landmarks.insert(28, {'x': right_ankle_x, 'y': right_ankle_y, 'z': 0.0, 'visibility': 1.0})
        
        # Fill remaining landmarks with reasonable positions
        while len(landmarks) < 33:
            landmarks.append({'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0})
        
        return landmarks[:33]  # Ensure exactly 33 landmarks
    
    def update_demo_frame(self):
        """Update demo animation frame with enhanced NEON WIRE filter"""
        # Create dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Generate demo landmarks
        landmarks = self.create_demo_landmarks(640, 480)
        
        # Apply the enhanced NEON WIRE filter
        filtered_frame = self.neon_filter.apply(frame, landmarks, 640, 480)
        
        # HORIZONTALLY MIRROR the frame to fix orientation
        filtered_frame = cv2.flip(filtered_frame, 1)
        
        # Convert to RGB
        frame_rgb = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
        
        # Convert to QImage
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Display
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        
        self.frame_count += 1
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Escape:
            print("ESC key pressed - closing")
            self.close()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = DemoMotionMirror()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
