import numpy as np
import random
import math

class Particle:
    def __init__(self, x, y, vx=0, vy=0, color=(255, 255, 255), lifetime=60, size=3):
        self.x = x
        self.y = y
        self.vx = vx  # velocity x
        self.vy = vy  # velocity y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = 0.1
        
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Apply gravity
        self.lifetime -= 1
        
        # Apply friction
        self.vx *= 0.99
        self.vy *= 0.99
        
    def get_alpha(self):
        """Get alpha value based on remaining lifetime"""
        return int(255 * (self.lifetime / self.max_lifetime))
    
    def is_alive(self):
        """Check if particle is still alive"""
        return self.lifetime > 0

class ParticleSystem:
    def __init__(self, max_particles=5000):
        self.particles = []
        self.max_particles = max_particles
        
    def emit(self, x, y, vx=0, vy=0, color=(255, 255, 255), count=1, lifetime=60, size=3):
        """Emit particles at position"""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                # Add some randomness to velocity
                random_vx = vx + random.uniform(-2, 2)
                random_vy = vy + random.uniform(-2, 2)
                
                particle = Particle(x, y, random_vx, random_vy, color, lifetime, size)
                self.particles.append(particle)
    
    def emit_burst(self, x, y, count=50, speed=5, color=(255, 255, 255)):
        """Emit particles in all directions (burst effect)"""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                angle = random.uniform(0, 2 * math.pi)
                speed_var = random.uniform(speed * 0.5, speed * 1.5)
                vx = math.cos(angle) * speed_var
                vy = math.sin(angle) * speed_var
                
                particle = Particle(x, y, vx, vy, color, random.randint(30, 60), random.randint(2, 5))
                self.particles.append(particle)
    
    def emit_cone(self, x, y, direction_angle, spread_angle=40, count=30, speed=4, color=(255, 255, 255)):
        """Emit particles in a cone shape"""
        spread_rad = math.radians(spread_angle)
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                angle = direction_angle + random.uniform(-spread_rad/2, spread_rad/2)
                speed_var = random.uniform(speed * 0.7, speed * 1.3)
                vx = math.cos(angle) * speed_var
                vy = math.sin(angle) * speed_var
                
                particle = Particle(x, y, vx, vy, color, random.randint(40, 80), random.randint(3, 8))
                self.particles.append(particle)
    
    def update(self):
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
    
    def get_count(self):
        """Get current particle count"""
        return len(self.particles)
