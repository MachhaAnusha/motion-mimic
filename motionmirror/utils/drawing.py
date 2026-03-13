import cv2
import numpy as np
import math

def draw_glow_line(img, pt1, pt2, color, thickness=3, glow_size=8):
    """Draw a line with glow effect"""
    # Draw glow layers
    for i in range(glow_size, 0, -1):
        alpha = int(50 * (1 - i/glow_size))
        glow_color = (*color, alpha)
        glow_thickness = thickness + i * 2
        
        # Create temporary overlay for glow
        overlay = img.copy()
        cv2.line(overlay, pt1, pt2, color[:3], glow_thickness)
        
        # Apply Gaussian blur for glow effect
        blurred = cv2.GaussianBlur(overlay, (15, 15), i)
        
        # Blend with original
        cv2.addWeighted(img, 1.0, blurred, alpha * 0.01, 0, img)
    
    # Draw core line
    cv2.line(img, pt1, pt2, color, thickness)

def draw_glow_circle(img, center, radius, color, thickness=-1, glow_size=6):
    """Draw a circle with glow effect"""
    # Draw glow layers
    for i in range(glow_size, 0, -1):
        alpha = int(50 * (1 - i/glow_size))
        glow_radius = radius + i
        
        # Create temporary overlay for glow
        overlay = img.copy()
        cv2.circle(overlay, center, glow_radius, color[:3], thickness)
        
        # Apply Gaussian blur for glow effect
        blurred = cv2.GaussianBlur(overlay, (15, 15), i)
        
        # Blend with original
        cv2.addWeighted(img, 1.0, blurred, alpha * 0.01, 0, img)
    
    # Draw core circle
    cv2.circle(img, center, radius, color, thickness)

def draw_gradient_line(img, pt1, pt2, start_color, end_color, thickness=3):
    """Draw a line with gradient color"""
    # Calculate line length and direction
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    length = math.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return
    
    # Draw multiple segments with interpolated colors
    segments = max(10, int(length / 5))
    for i in range(segments):
        t = i / segments
        x = int(pt1[0] + dx * t)
        y = int(pt1[1] + dy * t)
        next_x = int(pt1[0] + dx * (t + 1/segments))
        next_y = int(pt1[1] + dy * (t + 1/segments))
        
        # Interpolate color
        color = [
            int(start_color[j] + (end_color[j] - start_color[j]) * t)
            for j in range(3)
        ]
        
        cv2.line(img, (x, y), (next_x, next_y), color, thickness)

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color"""
    import colorsys
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return tuple(int(c * 255) for c in rgb)

def draw_ribbon(img, points, start_color, end_color, max_thickness=8):
    """Draw a ribbon trail from points"""
    if len(points) < 2:
        return
    
    for i in range(len(points) - 1):
        # Calculate thickness based on position in trail
        thickness = int(max_thickness * (1 - i / len(points)))
        thickness = max(1, thickness)
        
        # Interpolate color
        t = i / (len(points) - 1)
        color = [
            int(start_color[j] + (end_color[j] - start_color[j]) * t)
            for j in range(3)
        ]
        
        # Add wave displacement
        wave_offset = math.sin(i * 0.3) * 2
        
        pt1 = (int(points[i][0] + wave_offset), int(points[i][1]))
        pt2 = (int(points[i+1][0] + wave_offset), int(points[i+1][1]))
        
        cv2.line(img, pt1, pt2, color, thickness)

def draw_ink_splash(img, x, y, color, size_range=(4, 15)):
    """Draw irregular ink splash shape"""
    # Create random ellipse for ink droplet
    width = np.random.randint(*size_range)
    height = np.random.randint(*size_range)
    angle = np.random.randint(0, 180)
    
    # Create points for rotated ellipse
    center = (x, y)
    axes = (width, height)
    
    # Draw filled ellipse
    cv2.ellipse(img, center, axes, angle, 0, 360, color, -1)
    
    # Add some smaller splatters around
    for _ in range(np.random.randint(2, 5)):
        offset_x = x + np.random.randint(-20, 20)
        offset_y = y + np.random.randint(-20, 20)
        small_size = np.random.randint(2, 6)
        cv2.circle(img, (offset_x, offset_y), small_size, color, -1)

def apply_scanline_effect(img, intensity=0.1):
    """Apply subtle scanline flicker effect"""
    height = img.shape[0]
    for y in range(0, height, 2):
        if np.random.random() < intensity:
            img[y, :] = img[y, :] * np.random.uniform(0.8, 1.0)
    
    return img
