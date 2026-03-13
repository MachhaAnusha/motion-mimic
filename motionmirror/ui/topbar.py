from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient

class CameraToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_on = False
        
        self.setFixedSize(120, 40)
        self.update_style()
        
        self.setText("CAMERA OFF")
        self.clicked.connect(self.toggle)
    
    def toggle(self):
        self.is_on = not self.is_on
        self.update_style()
        self.setText("CAMERA ON" if self.is_on else "CAMERA OFF")
    
    def update_style(self):
        if self.is_on:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #00f5ff;
                    border: none;
                    border-radius: 20px;
                    color: #000000;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00d4e0;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    border: 2px solid #555555;
                    border-radius: 20px;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #444444;
                    border-color: #00f5ff;
                }
            """)

class FPSCounter(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fps = 0
        
        self.setStyleSheet("""
            QLabel {
                color: #00f5ff;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 10px;
                background-color: #1a1a1a;
                border-radius: 5px;
            }
        """)
        
        self.setText("FPS: 0")
    
    def update_fps(self, fps):
        self.fps = fps
        self.setText(f"FPS: {fps}")

class TopBar(QWidget):
    camera_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # App title
        self.title = QLabel("MOTION MIRROR")
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title.setStyleSheet("""
            QLabel {
                color: #00f5ff;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Arial Black', sans-serif;
                text-shadow: 0 0 10px #00f5ff;
            }
        """)
        layout.addWidget(self.title)
        
        # Spacer
        layout.addStretch()
        
        # Camera toggle button
        self.camera_button = CameraToggleButton()
        self.camera_button.clicked.connect(self.on_camera_toggle)
        layout.addWidget(self.camera_button)
        
        # FPS counter
        self.fps_counter = FPSCounter()
        layout.addWidget(self.fps_counter)
        
        # Set top bar style
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-bottom: 1px solid #333333;
            }
        """)
    
    def on_camera_toggle(self):
        """Handle camera toggle"""
        is_on = self.camera_button.is_on
        self.camera_toggled.emit(is_on)
    
    def update_fps(self, fps):
        """Update FPS counter"""
        self.fps_counter.update_fps(fps)
    
    def set_camera_state(self, is_on):
        """Set camera state programmatically"""
        if self.camera_button.is_on != is_on:
            self.camera_button.toggle()
