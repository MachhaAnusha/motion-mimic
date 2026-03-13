"""
AuraMotion Studio - Professional Motion Visualization Application
Main application entry point
"""

import sys
import os
import cv2
import numpy as np
import pygame
import tkinter as tk
from tkinter import ttk, Canvas, Frame, Label, Button, Scale
from PIL import Image, ImageTk
import threading
import time
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera import Camera
from pose_detector import PoseDetector
from filters import *
from gestures.gesture_detector import GestureDetector


class AuraMotionStudio:
    def __init__(self):
        # Initialize core components
        self.width = 1280
        self.height = 720
        self.running = True
        self.camera_on = False
        self.mirror_mode = True
        self.pip_visible = True
        
        # Initialize camera and pose detection
        self.camera = Camera()
        self.pose_detector = PoseDetector()
        
        # Initialize filters
        self.filters = {
            1: NeonPhantomFilter(self.width, self.height),
            2: AuraBurstFilter(self.width, self.height),
            3: BoneCarnivalFilter(self.width, self.height),
            4: EchoWalkerFilter(self.width, self.height),
            5: SilkTrailsFilter(self.width, self.height),
            6: InkBrawlerFilter(self.width, self.height)
        }
        self.current_filter = 1
        
        # UI setup
        self.setup_pygame()
        self.setup_tkinter_ui()
        
        # Performance tracking
        self.fps = 0
        self.last_fps_time = time.time()
        self.frame_count = 0
        
        # Start main loop
        self.main_loop()
        
    def setup_pygame(self):
        """Initialize Pygame for main canvas"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AuraMotion Studio")
        self.clock = pygame.time.Clock()
        
    def setup_tkinter_ui(self):
        """Setup Tkinter control panel"""
        self.root = tk.Tk()
        self.root.title("AuraMotion Studio Controls")
        self.root.geometry("300x800")
        self.root.configure(bg='#0a0a0f')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme colors
        style.configure('Dark.TFrame', background='#111118')
        style.configure('Dark.TLabel', background='#111118', foreground='#ffffff')
        style.configure('Dark.TButton', background='#1a1a2e', foreground='#ffffff')
        style.map('Dark.TButton', background=[('active', '#16213e')])
        
        # Main container
        main_frame = Frame(self.root, bg='#0a0a0f')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App title
        title_label = Label(main_frame, text="⚡ AURAMOTION STUDIO", 
                          font=("Arial", 16, "bold"), 
                          bg='#0a0a0f', fg='#00ffff')
        title_label.pack(pady=(0, 20))
        
        # Camera controls
        camera_frame = Frame(main_frame, bg='#111118', relief=tk.RAISED, bd=2)
        camera_frame.pack(fill=tk.X, pady=10)
        
        self.camera_button = Button(camera_frame, text="📷 CAMERA ON", 
                                  command=self.toggle_camera,
                                  font=("Arial", 12, "bold"),
                                  bg='#00ff00', fg='#000000',
                                  width=20, height=2)
        self.camera_button.pack(pady=10)
        
        self.mirror_button = Button(camera_frame, text="🔄 MIRROR: ON", 
                                   command=self.toggle_mirror,
                                   font=("Arial", 10),
                                   bg='#1a1a2e', fg='#ffffff',
                                   width=20)
        self.mirror_button.pack(pady=5)
        
        # Filter selector
        filter_frame = Frame(main_frame, bg='#111118', relief=tk.RAISED, bd=2)
        filter_frame.pack(fill=tk.X, pady=10)
        
        Label(filter_frame, text="VISUAL FILTERS", 
              font=("Arial", 12, "bold"),
              bg='#111118', fg='#ffffff').pack(pady=10)
        
        # Filter buttons
        filter_info = {
            1: ("Neon Phantom", "#ff00ff"),
            2: ("Aura Burst", "#00ff00"),
            3: ("Bone Carnival", "#ffa500"),
            4: ("Echo Walker", "#00ffff"),
            5: ("Silk Trails", "#ff69b4"),
            6: ("Ink Brawler", "#ff0000")
        }
        
        for num, (name, color) in filter_info.items():
            btn = Button(filter_frame, text=f"{num}. {name}", 
                        command=lambda n=num: self.set_filter(n),
                        font=("Arial", 10),
                        bg='#1a1a2e', fg=color,
                        width=18)
            btn.pack(pady=2)
            
        # Intensity control
        intensity_frame = Frame(main_frame, bg='#111118', relief=tk.RAISED, bd=2)
        intensity_frame.pack(fill=tk.X, pady=10)
        
        Label(intensity_frame, text="INTENSITY", 
              font=("Arial", 12, "bold"),
              bg='#111118', fg='#ffffff').pack(pady=10)
        
        self.intensity_scale = Scale(intensity_frame, from_=0.1, to=1.0, 
                                    resolution=0.1, orient=tk.HORIZONTAL,
                                    command=self.update_intensity,
                                    bg='#1a1a2e', fg='#ffffff',
                                    troughcolor='#0a0a0f',
                                    length=250)
        self.intensity_scale.set(1.0)
        self.intensity_scale.pack(pady=5)
        
        # FPS display
        self.fps_label = Label(main_frame, text="FPS: 0", 
                              font=("Arial", 10),
                              bg='#0a0a0f', fg='#00ff00')
        self.fps_label.pack(pady=10)
        
        # Action buttons
        action_frame = Frame(main_frame, bg='#111118', relief=tk.RAISED, bd=2)
        action_frame.pack(fill=tk.X, pady=10)
        
        Button(action_frame, text="🗑️ CLEAR CANVAS", 
               command=self.clear_canvas,
               font=("Arial", 10),
               bg='#1a1a2e', fg='#ffffff',
               width=18).pack(pady=5)
        
        Button(action_frame, text="📷 TOGGLE PIP", 
               command=self.toggle_pip,
               font=("Arial", 10),
               bg='#1a1a2e', fg='#ffffff',
               width=18).pack(pady=5)
        
        # Instructions
        info_frame = Frame(main_frame, bg='#111118', relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=10)
        
        instructions = """KEYBOARD SHORTCUTS:
1-6: Switch filters
Space: Pause/Resume
C: Clear canvas
M: Mirror mode
Escape: Quit"""
        
        Label(info_frame, text=instructions, 
              font=("Arial", 9),
              bg='#111118', fg='#aaaaaa',
              justify=tk.LEFT).pack(pady=10, padx=10)
        
        # Position Tkinter window
        self.root.geometry("+{}+0".format(self.width + 50))
        
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.camera_on:
            self.camera.stop()
            self.camera_on = False
            self.camera_button.config(text="📷 CAMERA OFF", bg='#ff0000', fg='#ffffff')
        else:
            if self.camera.start():
                self.camera_on = True
                self.camera_button.config(text="📷 CAMERA ON", bg='#00ff00', fg='#000000')
                
    def toggle_mirror(self):
        """Toggle mirror mode"""
        self.mirror_mode = not self.mirror_mode
        status = "ON" if self.mirror_mode else "OFF"
        self.mirror_button.config(text=f"🔄 MIRROR: {status}")
        
    def toggle_pip(self):
        """Toggle PiP camera box"""
        self.pip_visible = not self.pip_visible
        
    def set_filter(self, filter_num: int):
        """Set active filter"""
        if filter_num in self.filters:
            self.current_filter = filter_num
            # Reset all filters when switching
            for f in self.filters.values():
                f.reset()
                
    def update_intensity(self, value):
        """Update filter intensity"""
        intensity = float(value)
        for filter_obj in self.filters.values():
            filter_obj.set_intensity(intensity)
            
    def clear_canvas(self):
        """Clear current filter canvas"""
        if self.current_filter in self.filters:
            current_filter = self.filters[self.current_filter]
            if hasattr(current_filter, 'clear_canvas'):
                current_filter.clear_canvas()
            else:
                current_filter.reset()
                
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process camera frame through current filter"""
        if not self.camera_on or frame is None:
            return np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
        # Mirror frame if enabled
        if self.mirror_mode:
            frame = cv2.flip(frame, 1)
            
        # Detect pose
        landmarks, pose_landmarks, velocities, holistic_results = self.pose_detector.detect(frame)
        
        # Apply current filter
        if self.current_filter in self.filters:
            filter_obj = self.filters[self.current_filter]
            result = filter_obj.apply(frame, landmarks, velocities, 
                                    holistic_results=holistic_results)
            return result
            
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
    def draw_pip_camera(self, surface: pygame.Surface, frame: np.ndarray):
        """Draw Picture-in-Picture camera feed"""
        if not self.pip_visible or frame is None:
            return
            
        # Resize frame for PiP
        pip_width, pip_height = 240, 180
        pip_x = self.width - pip_width - 20
        pip_y = self.height - pip_height - 20
        
        # Resize and convert frame
        small_frame = cv2.resize(frame, (pip_width, pip_height))
        
        # Convert BGR to RGB
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Create pygame surface
        pip_surface = pygame.surfarray.make_surface(small_frame.swapaxes(0, 1))
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), 
                       (pip_x-2, pip_y-2, pip_width+4, pip_height+4), 2)
        
        # Draw camera feed
        surface.blit(pip_surface, (pip_x, pip_y))
        
    def update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
            self.fps_label.config(text=f"FPS: {self.fps}")
            
    def handle_pygame_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    filter_num = event.key - pygame.K_0
                    self.set_filter(filter_num)
                elif event.key == pygame.K_SPACE:
                    self.toggle_camera()
                elif event.key == pygame.K_c:
                    self.clear_canvas()
                elif event.key == pygame.K_m:
                    self.toggle_mirror()
                    
    def main_loop(self):
        """Main application loop"""
        while self.running:
            # Handle events
            self.handle_pygame_events()
            
            # Get camera frame
            frame_data = None
            if self.camera_on:
                # Try to get latest frame
                try:
                    # Process frame through filter
                    processed_frame = self.process_frame(None)  # Will get frame internally
                except:
                    processed_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            else:
                processed_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                
            # Convert to pygame surface
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            pygame_surface = pygame.surfarray.make_surface(processed_frame.swapaxes(0, 1))
            
            # Draw to screen
            self.screen.blit(pygame_surface, (0, 0))
            
            # Draw PiP if camera is on
            if self.camera_on:
                # Get raw frame for PiP
                try:
                    ret, raw_frame = self.camera.cap.read()
                    if ret:
                        self.draw_pip_camera(self.screen, raw_frame)
                except:
                    pass
                    
            # Update display
            pygame.display.flip()
            self.clock.tick(30)  # Target 30 FPS
            
            # Update FPS
            self.update_fps()
            
            # Update Tkinter
            try:
                self.root.update()
            except:
                self.running = False
                
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources"""
        self.camera.stop()
        self.pose_detector.close()
        pygame.quit()
        try:
            self.root.destroy()
        except:
            pass


if __name__ == "__main__":
    app = AuraMotionStudio()
