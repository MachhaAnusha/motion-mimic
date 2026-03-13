"""
Individual particle class for particle effects
"""

import numpy as np
import random
import math
from typing import Tuple, Optional


class Particle:
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0, 
                 color: Tuple[int, int, int] = (255, 255, 255), 
                 size: float = 3.0, lifetime: float = 2.0):
        self.x = x
        self.y = y
        self.vx = vx  # velocity x
        self.vy = vy  # velocity y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1
        self.friction = 0.98
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        
    def update(self, dt: float = 0.016):
        """Update particle position and properties"""
        # Apply physics
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Update lifetime
        self.lifetime -= dt
        
        # Update pulse for glowing effect
        self.pulse_phase += 0.1
        
    def is_alive(self) -> bool:
        """Check if particle is still alive"""
        return self.lifetime > 0
        
    def get_alpha(self) -> float:
        """Get particle alpha based on lifetime"""
        return max(0, min(255, (self.lifetime / self.max_lifetime) * 255))
        
    def get_size(self) -> float:
        """Get current particle size with pulse effect"""
        pulse = 1.0 + 0.2 * math.sin(self.pulse_phase)
        return self.size * pulse
        
    def apply_force(self, fx: float, fy: float):
        """Apply force to particle"""
        self.vx += fx
        self.vy += fy
        
    def explode(self, force: float = 10.0):
        """Make particle explode outward"""
        angle = random.uniform(0, 2 * math.pi)
        self.vx = force * math.cos(angle)
        self.vy = force * math.sin(angle)
        
    def implode(self, center_x: float, center_y: float, force: float = 5.0):
        """Make particle move toward center"""
        dx = center_x - self.x
        dy = center_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = (dx / dist) * force
            self.vy = (dy / dist) * force
