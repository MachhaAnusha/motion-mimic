"""
Particle system manager for handling multiple particles
"""

import numpy as np
import random
import math
from typing import List, Tuple, Optional
from .particle import Particle


class ParticleSystem:
    def __init__(self, max_particles: int = 5000):
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.color_themes = {
            'fire': [(255, 100, 0), (255, 200, 0), (255, 255, 100)],
            'ice': [(100, 200, 255), (150, 150, 255), (200, 100, 255)],
            'nature': [(100, 255, 100), (150, 255, 150), (200, 255, 200)],
            'cosmic': [(255, 100, 255), (200, 150, 255), (150, 200, 255)],
            'sunset': [(255, 150, 100), (255, 200, 150), (255, 250, 200)]
        }
        self.current_theme = 'fire'
        self.frozen = False
        self.imploding = False
        self.shrinking = False
        
    def add_particle(self, x: float, y: float, vx: float = 0, vy: float = 0,
                    color: Optional[Tuple[int, int, int]] = None, 
                    size: float = 3.0, lifetime: float = 2.0) -> bool:
        """Add a new particle to the system"""
        if len(self.particles) >= self.max_particles:
            return False
            
        if color is None:
            color = random.choice(self.color_themes[self.current_theme])
            
        particle = Particle(x, y, vx, vy, color, size, lifetime)
        self.particles.append(particle)
        return True
        
    def update(self, dt: float = 0.016):
        """Update all particles"""
        if self.frozen:
            return
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        
        # Update living particles
        for particle in self.particles:
            particle.update(dt)
            
            if self.imploding:
                # Apply implosion force toward center
                particle.implode(400, 300, 2.0)
            elif self.shrinking:
                # Apply shrinking force
                particle.implode(400, 300, 1.0)
                
    def create_burst(self, x: float, y: float, count: int = 50, 
                     force: float = 10.0, color: Optional[Tuple[int, int, int]] = None):
        """Create a burst of particles at position"""
        for _ in range(min(count, self.max_particles - len(self.particles))):
            if color is None:
                color = random.choice(self.color_themes[self.current_theme])
            particle = Particle(x, y, 0, 0, color, random.uniform(2, 5))
            particle.explode(force)
            self.particles.append(particle)
            
    def create_silhouette_particles(self, landmarks, bounding_box, density: int = 100):
        """Create particles within body silhouette"""
        if not landmarks or not bounding_box:
            return
            
        x_min, y_min, x_max, y_max = bounding_box
        
        # Create particles within bounding box
        for _ in range(density):
            if len(self.particles) >= self.max_particles:
                break
                
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)
            
            # Check if point is roughly within body shape (simplified)
            if self._is_in_body_region(x, y, landmarks):
                # Color based on body region
                color = self._get_region_color(x, y, landmarks)
                vx = random.uniform(-1, 1)
                vy = random.uniform(-1, 1)
                self.add_particle(x, y, vx, vy, color, random.uniform(2, 4))
                
    def _is_in_body_region(self, x: float, y: float, landmarks) -> bool:
        """Simplified check if point is within body region"""
        if not landmarks:
            return False
            
        # Find nearest landmark
        min_dist = float('inf')
        for landmark in landmarks:
            lx, ly = landmark.x, landmark.y
            dist = math.sqrt((x - lx*800)**2 + (y - ly*600)**2)
            min_dist = min(min_dist, dist)
            
        # Consider within body if close enough to any landmark
        return min_dist < 100
        
    def _get_region_color(self, x: float, y: float, landmarks) -> Tuple[int, int, int]:
        """Get color based on body region"""
        if not landmarks:
            return random.choice(self.color_themes[self.current_theme])
            
        # Simplified region detection
        if y < 200:  # Head/shoulders
            return random.choice([(255, 200, 200), (255, 150, 150)])
        elif y < 400:  # Torso
            return random.choice([(255, 150, 100), (255, 200, 100)])
        else:  # Legs
            return random.choice([(100, 150, 255), (150, 200, 255)])
            
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
        
    def freeze(self):
        """Freeze all particles"""
        self.frozen = True
        
    def unfreeze(self):
        """Unfreeze all particles"""
        self.frozen = False
        
    def implode(self):
        """Make all particles implode"""
        self.imploding = True
        
    def stop_implosion(self):
        """Stop implosion effect"""
        self.imploding = False
        
    def shrink(self):
        """Shrink particle field"""
        self.shrinking = True
        
    def stop_shrinking(self):
        """Stop shrinking effect"""
        self.shrinking = False
        
    def change_theme(self):
        """Cycle to next color theme"""
        themes = list(self.color_themes.keys())
        current_index = themes.index(self.current_theme)
        self.current_theme = themes[(current_index + 1) % len(themes)]
        
    def get_particle_count(self) -> int:
        """Get current particle count"""
        return len(self.particles)
