import { useState } from 'react';

const BrushSelector = ({ brushSize, setBrushSize, isMobile = false }) => {
  const presetSizes = [
    { label: 'XS', size: 2 },
    { label: 'S', size: 5 },
    { label: 'M', size: 10 },
    { label: 'L', size: 20 },
    { label: 'XL', size: 40 },
    { label: 'XXL', size: 60 },
  ];

  return (
    <div className={`toolbar ${isMobile ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-bold mb-3 text-green-400 ${isMobile ? 'text-center' : ''}`}>
        Brush Size
      </h3>
      
      {/* Preset Sizes */}
      <div className={`mb-4 ${isMobile ? 'flex justify-center space-x-2' : 'grid grid-cols-3 gap-2'}`}>
        {presetSizes.map((preset) => (
          <button
            key={preset.label}
            onClick={() => setBrushSize(preset.size)}
            className={`toolbar-button ${brushSize === preset.size ? 'active' : ''} ${
              isMobile ? 'px-3 py-1 text-xs' : ''
            }`}
          >
            {preset.label}
            {!isMobile && <span className="ml-1 text-xs">({preset.size}px)</span>}
          </button>
        ))}
      </div>

      {/* Custom Size Slider */}
      <div>
        <label className="block text-sm font-semibold mb-2 text-gray-300">
          Custom Size: {brushSize}px
        </label>
        <input
          type="range"
          min="1"
          max="100"
          value={brushSize}
          onChange={(e) => setBrushSize(parseInt(e.target.value))}
          className="w-full"
        />
        
        {/* Visual Preview */}
        <div className="mt-3 flex justify-center items-center h-16 bg-gray-800 rounded">
          <div
            className="rounded-full bg-green-400"
            style={{
              width: `${Math.min(brushSize, 60)}px`,
              height: `${Math.min(brushSize, 60)}px`,
              maxWidth: '60px',
              maxHeight: '60px',
            }}
          />
        </div>
      </div>

      {/* Brush Tips */}
      {!isMobile && (
        <div className="mt-4 text-xs text-gray-400">
          <p className="font-semibold mb-1">Tips:</p>
          <ul className="space-y-1">
            <li>• Use smaller sizes for details</li>
            <li>• Larger sizes for fills and backgrounds</li>
            <li>• Pressure sensitivity affects size</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default BrushSelector;
