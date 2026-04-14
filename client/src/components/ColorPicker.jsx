import { useState } from 'react';

const ColorPicker = ({ 
  selectedColor, 
  setSelectedColor, 
  opacity, 
  setOpacity, 
  neonGlow, 
  setNeonGlow,
  isMobile = false 
}) => {
  const [showCustomColor, setShowCustomColor] = useState(false);

  const presetColors = [
    '#39ff14', // Neon Green
    '#00d4ff', // Electric Blue
    '#ff1493', // Hot Pink
    '#ff4500', // Fire Orange
    '#ffff00', // Yellow
    '#ff00ff', // Magenta
    '#00ff00', // Lime
    '#ff6b6b', // Coral
    '#4ecdc4', // Turquoise
    '#95e1d3', // Mint
    '#f38181', // Salmon
    '#aa96da', // Lavender
    '#c0c0c0', // Chrome
    '#ffffff', // White
    '#000000', // Black
    '#8b4513', // Brown
  ];

  const graffitiPalettes = {
    'Old School': ['#ff0000', '#ffff00', '#0000ff', '#ffffff', '#000000'],
    'Neon': ['#39ff14', '#00d4ff', '#ff1493', '#ffff00', '#ff00ff'],
    'Pastel': ['#ffb3ba', '#bae1ff', '#ffffba', '#baffc9', '#ffdfba'],
    'Fire': ['#ff4500', '#ff6347', '#ff8c00', '#ffd700', '#ffff00'],
    'Chrome': ['#c0c0c0', '#d3d3d3', '#a9a9a9', '#808080', '#696969'],
    'Dark': ['#1a1a1a', '#2d2d2d', '#404040', '#595959', '#737373'],
  };

  const handlePaletteSelect = (paletteName) => {
    const colors = graffitiPalettes[paletteName];
    if (colors && colors.length > 0) {
      setSelectedColor(colors[0]);
    }
  };

  return (
    <div className={`toolbar ${isMobile ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-bold mb-3 text-green-400 ${isMobile ? 'text-center' : ''}`}>
        Colors
      </h3>
      
      {/* Preset Colors */}
      <div className="mb-4">
        <div className="color-palette">
          {presetColors.map((color) => (
            <button
              key={color}
              onClick={() => setSelectedColor(color)}
              className={`color-swatch ${selectedColor === color ? 'active' : ''}`}
              style={{ backgroundColor: color }}
              title={color}
            />
          ))}
        </div>
      </div>

      {/* Graffiti Palettes */}
      {!isMobile && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold mb-2 text-gray-300">Graffiti Palettes</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(graffitiPalettes).map((paletteName) => (
              <button
                key={paletteName}
                onClick={() => handlePaletteSelect(paletteName)}
                className="toolbar-button text-xs"
              >
                {paletteName}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Custom Color Picker */}
      <div className="mb-4">
        <button
          onClick={() => setShowCustomColor(!showCustomColor)}
          className="toolbar-button w-full text-sm"
        >
          {showCustomColor ? 'Hide' : 'Show'} Custom Color
        </button>
        {showCustomColor && (
          <div className="mt-2 flex items-center space-x-2">
            <input
              type="color"
              value={selectedColor}
              onChange={(e) => setSelectedColor(e.target.value)}
              className="w-full h-10 rounded cursor-pointer"
            />
            <input
              type="text"
              value={selectedColor}
              onChange={(e) => setSelectedColor(e.target.value)}
              className="w-24 p-1 text-xs bg-gray-800 border border-gray-700 rounded"
              placeholder="#000000"
            />
          </div>
        )}
      </div>

      {/* Opacity Slider */}
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-2 text-gray-300">
          Opacity: {opacity}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          value={opacity}
          onChange={(e) => setOpacity(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Neon Glow Toggle */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-gray-300">Neon Glow</label>
        <button
          onClick={() => setNeonGlow(!neonGlow)}
          className={`w-12 h-6 rounded-full transition-colors ${
            neonGlow ? 'bg-green-500' : 'bg-gray-600'
          }`}
        >
          <div
            className={`w-5 h-5 bg-white rounded-full transition-transform ${
              neonGlow ? 'translate-x-6' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>
    </div>
  );
};

export default ColorPicker;
