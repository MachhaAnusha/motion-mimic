import cv2
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

class Camera(QObject):
    frame_ready = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.thread = None
        self.fps = 0
        self.last_frame_time = time.time()
        self.frame_count = 0
        
    def start(self):
        """Start camera capture"""
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if self.cap.isOpened():
                self.running = True
                self.thread = threading.Thread(target=self._capture_loop)
                self.thread.daemon = True
                self.thread.start()
                return True
        return False
    
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Mirror the frame horizontally
                frame = cv2.flip(frame, 1)
                
                # Calculate FPS
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_frame_time >= 1.0:
                    self.fps = self.frame_count
                    self.frame_count = 0
                    self.last_frame_time = current_time
                
                # Emit frame with metadata
                frame_data = {
                    'frame': frame,
                    'fps': self.fps,
                    'timestamp': current_time
                }
                self.frame_ready.emit(frame_data)
            
            # Control frame rate to ~30 FPS
            time.sleep(1/30)
    
    def is_running(self):
        """Check if camera is running"""
        return self.running
    
    def get_fps(self):
        """Get current FPS"""
        return self.fps
