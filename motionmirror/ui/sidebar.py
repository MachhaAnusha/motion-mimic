from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient

class FilterButton(QPushButton):
    def __init__(self, icon, name, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.name = name
        self.is_active = False
        
        self.setFixedSize(80, 80)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 10px;
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                border-color: #00f5ff;
            }
            QPushButton:active {
                background-color: #00f5ff;
                border-color: #00f5ff;
            }
        """)
        
        self.setText(icon)
        self.setToolTip(name)
    
    def set_active(self, active):
        self.is_active = active
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #00f5ff;
                    border: 2px solid #00f5ff;
                    border-radius: 10px;
                    color: #000000;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    border: 2px solid #333333;
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    border-color: #00f5ff;
                }
            """)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw filter name below icon
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 8))
        
        text_rect = self.rect().adjusted(5, 50, -5, -5)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.name)

class Sidebar(QWidget):
    filter_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = "neon_wire"
        self.filter_buttons = {}
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("FILTERS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00f5ff;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Filter buttons
        filters = [
            ("🔵", "NEON WIRE", "neon_wire"),
            ("✨", "AURA", "aura"),
            ("💀", "CRYPTBORN", "cryptborn"),
            ("👥", "PHANTOM ECHO", "phantom_echo"),
            ("🎀", "SILK TRAILS", "silk_trails"),
            ("🥊", "INK SPLASH", "ink_splash")
        ]
        
        for icon, name, filter_id in filters:
            button = FilterButton(icon, name)
            button.clicked.connect(lambda checked, f=filter_id: self.select_filter(f))
            self.filter_buttons[filter_id] = button
            layout.addWidget(button)
        
        # Set first filter as active
        self.filter_buttons["neon_wire"].set_active(True)
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
        # Set sidebar style
        self.setFixedWidth(100)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-right: 1px solid #333333;
            }
        """)
    
    def select_filter(self, filter_id):
        """Handle filter selection"""
        # Deactivate all buttons
        for button in self.filter_buttons.values():
            button.set_active(False)
        
        # Activate selected button
        self.filter_buttons[filter_id].set_active(True)
        self.current_filter = filter_id
        
        # Emit signal
        self.filter_selected.emit(filter_id)
