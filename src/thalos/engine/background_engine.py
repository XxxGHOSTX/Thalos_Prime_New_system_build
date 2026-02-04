"""
3D Background Engine for THALOS Prime
Advanced particle system and dynamic background rendering
"""
import random
import math
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Particle:
    """3D Particle with physics properties"""
    x: float
    y: float
    z: float
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    life: float = 1.0
    size: float = 1.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)


class BackgroundEngine:
    """
    3D Background Engine with particle system
    Creates dynamic, animated backgrounds with various effects
    """
    
    def __init__(self, resolution: Tuple[int, int] = (1920, 1080),
                 particle_count: int = 10000, fps_target: int = 60):
        self.resolution = resolution
        self.max_particles = particle_count
        self.fps_target = fps_target
        self.particles: List[Particle] = []
        self.frame_count = 0
        self.running = False
        self.effect_mode = "stars"  # stars, waves, tunnel, swarm
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialize particle system"""
        for _ in range(self.max_particles):
            particle = self._create_particle()
            self.particles.append(particle)
    
    def _create_particle(self) -> Particle:
        """Create a new particle based on current effect mode"""
        if self.effect_mode == "stars":
            return self._create_star_particle()
        elif self.effect_mode == "waves":
            return self._create_wave_particle()
        elif self.effect_mode == "tunnel":
            return self._create_tunnel_particle()
        else:
            return self._create_swarm_particle()
    
    def _create_star_particle(self) -> Particle:
        """Create a star field particle"""
        return Particle(
            x=random.uniform(-self.resolution[0], self.resolution[0]),
            y=random.uniform(-self.resolution[1], self.resolution[1]),
            z=random.uniform(100, 1000),
            vz=-random.uniform(1, 5),  # Move towards camera
            life=1.0,
            size=random.uniform(0.5, 2.0),
            color=(random.uniform(0.7, 1.0), random.uniform(0.7, 1.0), random.uniform(0.9, 1.0))
        )
    
    def _create_wave_particle(self) -> Particle:
        """Create a wave effect particle"""
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, max(self.resolution) // 2)
        return Particle(
            x=radius * math.cos(angle),
            y=radius * math.sin(angle),
            z=random.uniform(0, 500),
            vx=math.cos(angle) * 0.5,
            vy=math.sin(angle) * 0.5,
            life=1.0,
            size=random.uniform(1.0, 3.0),
            color=(0.3, 0.7, 1.0)
        )
    
    def _create_tunnel_particle(self) -> Particle:
        """Create a tunnel effect particle"""
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(50, 300)
        return Particle(
            x=radius * math.cos(angle),
            y=radius * math.sin(angle),
            z=random.uniform(500, 2000),
            vz=-10,
            life=1.0,
            size=random.uniform(1.5, 4.0),
            color=(1.0, 0.5, 0.2)
        )
    
    def _create_swarm_particle(self) -> Particle:
        """Create a swarm behavior particle"""
        return Particle(
            x=random.uniform(-200, 200),
            y=random.uniform(-200, 200),
            z=random.uniform(100, 500),
            vx=random.uniform(-2, 2),
            vy=random.uniform(-2, 2),
            vz=random.uniform(-1, 1),
            life=1.0,
            size=random.uniform(0.8, 2.5),
            color=(0.5, 1.0, 0.5)
        )
    
    def start(self):
        """Start the background engine"""
        self.running = True
    
    def stop(self):
        """Stop the background engine"""
        self.running = False
    
    def set_effect(self, mode: str):
        """Change the visual effect mode"""
        if mode in ["stars", "waves", "tunnel", "swarm"]:
            self.effect_mode = mode
            # Recreate particles for new effect
            self.particles.clear()
            self._initialize_particles()
    
    def update(self, delta_time: float = 0.016):
        """Update particle system (call every frame)"""
        if not self.running:
            return
        
        self.frame_count += 1
        
        # Update each particle
        for particle in self.particles:
            # Update position
            particle.x += particle.vx
            particle.y += particle.vy
            particle.z += particle.vz
            
            # Update life
            particle.life -= 0.001
            
            # Apply effects based on mode
            if self.effect_mode == "stars":
                # Reset particles that moved past camera
                if particle.z < 10:
                    self._reset_star_particle(particle)
            
            elif self.effect_mode == "waves":
                # Apply wave motion
                time_factor = self.frame_count * 0.01
                particle.y += math.sin(particle.x * 0.01 + time_factor) * 0.5
            
            elif self.effect_mode == "tunnel":
                # Reset particles that moved past camera
                if particle.z < 10:
                    self._reset_tunnel_particle(particle)
            
            elif self.effect_mode == "swarm":
                # Apply flocking behavior (simplified)
                self._apply_swarm_behavior(particle)
        
        # Remove dead particles and create new ones
        self.particles = [p for p in self.particles if p.life > 0]
        while len(self.particles) < self.max_particles:
            self.particles.append(self._create_particle())
    
    def _reset_star_particle(self, particle: Particle):
        """Reset a star particle to the back"""
        particle.x = random.uniform(-self.resolution[0], self.resolution[0])
        particle.y = random.uniform(-self.resolution[1], self.resolution[1])
        particle.z = 1000
        particle.life = 1.0
    
    def _reset_tunnel_particle(self, particle: Particle):
        """Reset a tunnel particle"""
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(50, 300)
        particle.x = radius * math.cos(angle)
        particle.y = radius * math.sin(angle)
        particle.z = 2000
        particle.life = 1.0
    
    def _apply_swarm_behavior(self, particle: Particle):
        """Apply simple flocking behavior"""
        # Cohesion - move towards center
        center_x = sum(p.x for p in self.particles[:100]) / 100
        center_y = sum(p.y for p in self.particles[:100]) / 100
        
        particle.vx += (center_x - particle.x) * 0.0001
        particle.vy += (center_y - particle.y) * 0.0001
        
        # Limit velocity
        speed = math.sqrt(particle.vx**2 + particle.vy**2)
        if speed > 5:
            particle.vx = (particle.vx / speed) * 5
            particle.vy = (particle.vy / speed) * 5
    
    def get_render_data(self) -> List[dict]:
        """Get particles for rendering"""
        return [
            {
                'position': [p.x, p.y, p.z],
                'velocity': [p.vx, p.vy, p.vz],
                'life': p.life,
                'size': p.size,
                'color': p.color
            }
            for p in self.particles
        ]
    
    def get_stats(self) -> dict:
        """Get engine statistics"""
        return {
            'frame_count': self.frame_count,
            'particle_count': len(self.particles),
            'effect_mode': self.effect_mode,
            'resolution': self.resolution,
            'running': self.running
        }
