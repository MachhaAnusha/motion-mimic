import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class SimpleMotionMirror(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOTION MIRROR - Simple Test")
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
            font-size: 24px; 
            font-weight: bold;
            border: 2px solid #333;
        """)
        self.video_label.setText("MOTION MIRROR\n\nClick anywhere to start camera\n\nPress SPACE to toggle camera")
        layout.addWidget(self.video_label)
        
        # Make label clickable
        self.video_label.setMouseTracking(True)
        
        # Camera setup
        self.cap = None
        self.camera_on = False
        
        # Timer for video update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Animation timer for title
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate_title)
        self.anim_timer.start(100)
        self.glow_phase = 0
        
        print("MOTION MIRROR started - Click the window or press SPACE to start camera")
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on the main window"""
        print(f"Mouse clicked at: {event.pos()}")
        self.toggle_camera()
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Space:
            print("SPACE key pressed")
            self.toggle_camera()
        elif event.key() == Qt.Key.Key_Escape:
            print("ESC key pressed - closing")
            self.close()
        super().keyPressEvent(event)
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        print(f"Toggling camera - Current state: {self.camera_on}")
        if not self.camera_on:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_on = True
                self.timer.start(33)  # ~30 FPS
                print("Camera started")
            else:
                print("Failed to open camera")
        except Exception as e:
            print(f"Camera error: {e}")
    
    def stop_camera(self):
        """Stop camera capture"""
        self.camera_on = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Camera stopped")
    
    def update_frame(self):
        """Update video frame"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Mirror the frame
                frame = cv2.flip(frame, 1)
                
                # Add neon effect
                frame = self.add_neon_effect(frame)
                
                # Convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
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
            else:
                print("Failed to grab frame")
    
    def add_neon_effect(self, frame):
        """Add simple neon glow effect"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Find edges with lower threshold for more detection
        edges = cv2.Canny(gray, 30, 100)
        
        # Create multiple glow layers
        neon_frame = frame.copy()
        
        # First glow layer - thick cyan
        glow1 = cv2.dilate(edges, None, iterations=3)
        glow1 = cv2.GaussianBlur(glow1, (21, 21), 0)
        neon_frame[glow1 > 0] = [0, 255, 255]  # Cyan
        
        # Second glow layer - thinner white
        glow2 = cv2.dilate(edges, None, iterations=1)
        glow2 = cv2.GaussianBlur(glow2, (9, 9), 0)
        neon_frame[glow2 > 0] = [255, 255, 255]  # White
        
        # Original edges in bright cyan
        neon_frame[edges > 0] = [0, 200, 255]  # Bright cyan
        
        return neon_frame
    
    def animate_title(self):
        """Animate title when camera is off"""
        if not self.camera_on:
            # Steady white text instead of pulsing
            self.video_label.setStyleSheet("background-color: black; color: white; font-size: 24px; font-weight: bold;")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.stop_camera()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = SimpleMotionMirror()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
