# ⚡ AuraMotion Studio

A professional desktop application for real-time motion visualization and artistic effects using computer vision.

## 🎨 Features

### 6 Artistic Filters

1. **Neon Phantom** - Glowing neon skeleton with pulsing joints and scanline effects
2. **Aura Burst** - Particle art with gesture controls (freeze, implode, color themes)
3. **Bone Carnival** - Cartoon Halloween skeleton with ambient animations
4. **Echo Walker** - Motion trail effects creating time-lapse ghost echoes
5. **Silk Trails** - Smooth ribbon trails following major joints with turbulence
6. **Ink Brawler** - Combat detection with ink splatter effects and persistent canvas

### 🎛️ Professional UI

- **Modern dark theme** with neon accents
- **Real-time control panel** with filter selection
- **Picture-in-Picture camera** showing raw feed
- **Intensity controls** for fine-tuning effects
- **FPS counter** and performance monitoring
- **Keyboard shortcuts** for quick access

### 🎮 Interactive Controls

- **Gesture controls** in Aura Burst filter:
  - ✋ Open palm: Freeze particles
  - ✊ Closed fist: Implode particles
  - 👆 Point up: Change color theme
  - 🤏 Pinch: Shrink particle field
  - 🙌 Two hands up: Full-screen explosion

- **Keyboard shortcuts:**
  - `1-6`: Switch filters
  - `Space`: Toggle camera
  - `C`: Clear canvas
  - `M`: Mirror mode
  - `Escape`: Quit

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Webcam
- Windows/macOS/Linux

### Quick Start

1. **Clone or download** the project
2. **Run the launcher:**
   - Windows: Double-click `run.bat`
   - macOS/Linux: Run `./run.sh` in terminal

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python auramotion_studio.py
```

## 📋 Dependencies

```
opencv-python>=4.8.0      # Camera processing
mediapipe>=0.10.0         # Pose/hand detection
numpy>=1.24.0             # Mathematical operations
pygame>=2.5.0             # Main rendering canvas
PyQt6>=6.5.0              # UI framework
scipy>=1.10.0             # Advanced calculations
Pillow>=10.0.0            # Image processing
```

## 🎯 Usage Guide

### Getting Started

1. **Launch the application** using the launcher script
2. **Click "CAMERA ON"** to activate your webcam
3. **Step into frame** and see the magic happen!
4. **Select filters** using number keys or UI buttons
5. **Adjust intensity** with the slider for subtle or dramatic effects

### Filter-Specific Tips

#### Neon Phantom
- Stand still for clean neon lines
- Move quickly for intensified glow effects
- Perfect for dance performances

#### Aura Burst
- Use hand gestures for interactive control
- Slow movements create flowing particles
- Fast movements trigger explosive bursts

#### Bone Carnival
- Enjoy the Halloween atmosphere
- Watch for flying bats and twinkling stars
- Movement adds wobble animations

#### Echo Walker
- Create beautiful time-lapse effects
- Dance for dramatic ghost trails
- Stand still for subtle aura buildup

#### Silk Trails
- Move arms and legs for ribbon creation
- Fast movements create thick trails
- Perfect for fluid dance routines

#### Ink Brawler
- Punch and kick for ink explosions
- Build up persistent ink artwork
- Clear canvas to start fresh

## 🏗️ Project Structure

```
motionmirror/
├── auramotion_studio.py     # Main application
├── camera.py                # Camera management
├── pose_detector.py         # MediaPipe pose detection
├── filters/                 # Visual effects
│   ├── base_filter.py       # Base filter class
│   ├── neon_phantom.py      # Filter 1
│   ├── aura_burst.py        # Filter 2
│   ├── bone_carnival.py     # Filter 3
│   ├── echo_walker.py       # Filter 4
│   ├── silk_trails.py       # Filter 5
│   └── ink_brawler.py       # Filter 6
├── particles/               # Particle system
│   ├── particle.py          # Individual particle
│   └── particle_system.py   # Particle manager
├── gestures/               # Gesture detection
│   └── gesture_detector.py  # Hand gesture recognition
├── ui/                     # UI components
├── utils/                  # Utility functions
├── requirements.txt         # Dependencies
├── run.bat                 # Windows launcher
├── run.sh                  # Unix launcher
└── README.md              # This file
```

## 🎨 Customization

### Adding New Filters

1. **Create a new filter class** inheriting from `BaseFilter`
2. **Implement the `apply()` method** with your visualization logic
3. **Add to the filter dictionary** in `auramotion_studio.py`
4. **Update the UI** to include your new filter

### Modifying Colors

Each filter has customizable color schemes. Modify the color dictionaries in individual filter files to create your own themes.

## 🐛 Troubleshooting

### Common Issues

**Camera not detected:**
- Ensure webcam is connected and not used by other applications
- Check camera permissions in system settings
- Try restarting the application

**Low performance:**
- Close other applications using the camera
- Reduce intensity slider
- Ensure graphics drivers are up to date

**Gesture controls not working:**
- Ensure good lighting conditions
- Keep hands visible in camera frame
- Stand at appropriate distance (3-6 feet)

### Performance Tips

- **Target 30 FPS** for smooth animation
- **Close background applications** for better performance
- **Use good lighting** for better pose detection
- **Ensure stable camera position** for consistent tracking

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 🙏 Acknowledgments

- **MediaPipe** for pose and hand detection
- **OpenCV** for computer vision processing
- **Pygame** for real-time rendering
- **PyQt6** for modern UI components

---

**Enjoy creating motion art with AuraMotion Studio! ✨**
