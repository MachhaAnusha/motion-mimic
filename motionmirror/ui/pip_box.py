from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import cv2
import numpy as np

class PIPBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_visible = True
        self.current_frame = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set fixed size and position
        self.setFixedSize(200, 150)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                border: 2px solid #00f5ff;
                border-radius: 5px;
                background-color: #000000;
            }
        """)
    
    def update_frame(self, frame):
        """Update the PIP frame"""
        if frame is not None and self.is_visible:
            # Resize frame to PIP dimensions
            resized_frame = cv2.resize(frame, (196, 146))  # Account for border
            
            # Convert BGR to RGB
            if len(resized_frame.shape) == 3:
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            self.current_frame = resized_frame
            self.update()
    
    def toggle_visibility(self):
        """Toggle PIP box visibility"""
        self.is_visible = not self.is_visible
        self.setVisible(self.is_visible)
    
    def paintEvent(self, event):
        """Custom paint event"""
        super().paintEvent(event)
        
        if not self.is_visible:
            return
        
        painter = QPainter(self)
        
        # Draw frame if available
        if self.current_frame is not None:
            # Convert numpy array to QImage
            height, width, channel = self.current_frame.shape
            bytes_per_line = 3 * width
            
            from PyQt6.QtGui import QImage
            q_image = QImage(self.current_frame.data, width, height, 
                           bytes_per_line, QImage.Format.Format_RGB888)
            
            # Draw image centered
            painter.drawImage(2, 2, q_image)  # Account for border
        else:
            # Draw placeholder
            painter.fillRect(2, 2, 196, 146, QColor(20, 20, 20))
        
        # Draw "LIVE" label with red dot
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # Red dot
        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(QPen(QColor(255, 0, 0), 1))
        painter.drawEllipse(10, 10, 8, 8)
        
        # LIVE text
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(25, 18, "LIVE")
    
    def mousePressEvent(self, event):
        """Handle mouse click to toggle visibility"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_visibility()
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.setStyleSheet("""
            QWidget {
                border: 2px solid #ffffff;
                border-radius: 5px;
                background-color: #000000;
            }
        """)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.setStyleSheet("""
            QWidget {
                border: 2px solid #00f5ff;
                border-radius: 5px;
                background-color: #000000;
            }
        """)
