import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QImage

from camera import Camera
from pose_detector import PoseDetector
from ui.sidebar import Sidebar
from ui.topbar import TopBar
from ui.pip_box import PIPBox

# Import all filters
from filters.neon_wire import NeonWireFilter
from filters.aura import AuraFilter
from filters.cryptborn import CryptbornFilter
from filters.phantom_echo import PhantomEchoFilter
from filters.silk_trails import SilkTrailsFilter
from filters.ink_splash import InkSplashFilter

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = None
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: #000000;")
    
    def update_frame(self, frame):
        """Update the canvas with new frame"""
        self.current_frame = frame.copy() if frame is not None else None
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        
        if self.current_frame is not None:
            # Convert numpy array to QImage
            height, width, channel = self.current_frame.shape
            bytes_per_line = 3 * width
            
            q_image = QImage(self.current_frame.data, width, height, 
                           bytes_per_line, QImage.Format.Format_RGB888)
            
            # Draw image centered and scaled to fit
            widget_size = self.size()
            scaled_image = q_image.scaled(widget_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation)
            
            x = (widget_size.width() - scaled_image.width()) // 2
            y = (widget_size.height() - scaled_image.height()) // 2
            
            painter.drawImage(x, y, scaled_image)
        else:
            # Draw app logo/name when camera is off
            painter.setPen(QColor(0, 245, 255))
            painter.setFont(QFont("Arial Black", 48, QFont.Weight.Bold))
            
            text = "MOTION MIRROR"
            text_rect = self.rect()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

class MotionMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.pose_detector = None
        self.current_filter = None
        self.filters = {}
        self.camera_on = False
        
        self.init_components()
        self.init_ui()
        self.init_filters()
        self.select_filter("neon_wire")
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(33)  # ~30 FPS
        
        # Setup animation timer for title when camera is off
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_title)
        self.animation_timer.start(100)
        self.title_glow = 0
    
    def init_components(self):
        """Initialize core components"""
        self.camera = Camera()
        self.pose_detector = PoseDetector()
        
        # Connect camera signal
        self.camera.frame_ready.connect(self.process_frame)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MOTION MIRROR")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create vertical layout for main content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        self.top_bar = TopBar()
        self.top_bar.camera_toggled.connect(self.toggle_camera)
        content_layout.addWidget(self.top_bar)
        
        # Canvas area with PIP overlay
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = Canvas()
        canvas_layout.addWidget(self.canvas)
        
        # PIP box (positioned over canvas)
        self.pip_box = PIPBox(self.canvas)
        self.pip_box.move(self.canvas.width() - 210, self.canvas.height() - 160)
        
        content_layout.addWidget(canvas_container)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.filter_selected.connect(self.select_filter)
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(content_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        
        # Show maximized
        self.showMaximized()
    
    def init_filters(self):
        """Initialize all filters"""
        self.filters = {
            "neon_wire": NeonWireFilter(),
            "aura": AuraFilter(),
            "cryptborn": CryptbornFilter(),
            "phantom_echo": PhantomEchoFilter(),
            "silk_trails": SilkTrailsFilter(),
            "ink_splash": InkSplashFilter()
        }
    
    def select_filter(self, filter_id):
        """Select active filter"""
        if filter_id in self.filters:
            self.current_filter = self.filters[filter_id]
    
    def toggle_camera(self, is_on):
        """Toggle camera on/off"""
        self.camera_on = is_on
        
        if is_on:
            if self.camera.start():
                print("Camera started successfully")
            else:
                print("Failed to start camera")
                self.top_bar.set_camera_state(False)
        else:
            self.camera.stop()
            print("Camera stopped")
    
    def process_frame(self, frame_data):
        """Process camera frame"""
        frame = frame_data['frame']
        fps = frame_data['fps']
        
        # Update FPS counter
        self.top_bar.update_fps(fps)
        
        # Update PIP box
        self.pip_box.update_frame(frame)
        
        # Detect pose
        landmarks, _ = self.pose_detector.detect(frame)
        
        # If no pose detected, create demo landmarks for testing
        if not landmarks:
            landmarks = self.create_demo_landmarks(frame.shape[1], frame.shape[0])
        
        # Apply current filter
        if self.current_filter and landmarks:
            height, width = frame.shape[:2]
            filtered_frame = self.current_filter.apply(frame, landmarks, width, height)
            
            # Convert BGR to RGB for display
            if len(filtered_frame.shape) == 3:
                filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
            
            self.canvas.update_frame(filtered_frame)
        else:
            # Show black canvas when no landmarks detected
            black_frame = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)
            self.canvas.update_frame(black_frame)
    
    def create_demo_landmarks(self, width, height):
        """Create demo pose landmarks for testing when pose detection fails"""
        import time
        import math
        
        # Create a simple waving figure
        t = time.time()
        
        # Basic pose structure (simplified 33 landmarks)
        landmarks = []
        
        # Head and face (landmarks 0-10)
        for i in range(11):
            landmarks.append({
                'x': 0.5 + math.sin(t + i) * 0.05,
                'y': 0.2 + i * 0.02,
                'z': 0.0,
                'visibility': 1.0
            })
        
        # Shoulders (11-12)
        landmarks.append({'x': 0.4, 'y': 0.35, 'z': 0.0, 'visibility': 1.0})  # Left shoulder
        landmarks.append({'x': 0.6, 'y': 0.35, 'z': 0.0, 'visibility': 1.0})  # Right shoulder
        
        # Arms with waving motion
        wave_angle = math.sin(t * 2) * 0.3
        landmarks.append({'x': 0.35, 'y': 0.45, 'z': 0.0, 'visibility': 1.0})  # Left elbow
        landmarks.append({'x': 0.65 + wave_angle, 'y': 0.45 - abs(wave_angle) * 0.3, 'z': 0.0, 'visibility': 1.0})  # Right elbow
        landmarks.append({'x': 0.3, 'y': 0.55, 'z': 0.0, 'visibility': 1.0})  # Left wrist
        landmarks.append({'x': 0.7 + wave_angle * 1.5, 'y': 0.35 - abs(wave_angle) * 0.5, 'z': 0.0, 'visibility': 1.0})  # Right wrist
        
        # Hands and fingers (15-22)
        for i in range(8):
            base_x = 0.3 if i < 4 else 0.7 + wave_angle * 1.5
            base_y = 0.55 if i < 4 else 0.35 - abs(wave_angle) * 0.5
            landmarks.append({
                'x': base_x + (i % 4) * 0.02,
                'y': base_y + (i % 4) * 0.02,
                'z': 0.0,
                'visibility': 1.0
            })
        
        # Hips and legs (23-32)
        landmarks.append({'x': 0.45, 'y': 0.6, 'z': 0.0, 'visibility': 1.0})  # Left hip
        landmarks.append({'x': 0.55, 'y': 0.6, 'z': 0.0, 'visibility': 1.0})  # Right hip
        
        # Legs
        for i in range(10):
            is_left = i < 5
            base_x = 0.45 if is_left else 0.55
            base_y = 0.6 + i * 0.08
            landmarks.append({
                'x': base_x + math.sin(t + i) * 0.02,
                'y': base_y,
                'z': 0.0,
                'visibility': 1.0
            })
        
        return landmarks
    
    def update_frame(self):
        """Main update loop"""
        if not self.camera_on:
            # Show animated title when camera is off
            self.canvas.update_frame(None)
    
    def animate_title(self):
        """Animate title glow when camera is off"""
        if not self.camera_on:
            self.title_glow = (self.title_glow + 10) % 360
            self.canvas.update()
    
    def keyPressEvent(self, event):
        """Handle key presses"""
        if event.key() == Qt.Key.Key_C:
            # Clear ink splash canvas
            if self.current_filter and hasattr(self.current_filter, 'clear_canvas'):
                self.current_filter.clear_canvas()
                print("Canvas cleared")
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.camera:
            self.camera.stop()
        if self.pose_detector:
            self.pose_detector.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MotionMirrorApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
