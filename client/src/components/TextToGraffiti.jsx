import { useState } from 'react';

const TextToGraffiti = ({ fabricCanvas, moderateText }) => {
  const [text, setText] = useState('');
  const [graffitiStyle, setGraffitiStyle] = useState('bubble');
  const [fontSize, setFontSize] = useState(48);
  const [textColor, setTextColor] = useState('#39ff14');
  const [isGenerating, setIsGenerating] = useState(false);

  const graffitiStyles = [
    { id: 'bubble', name: 'Bubble', description: 'Rounded, bubbly letters' },
    { id: 'wildstyle', name: 'Wildstyle', description: 'Complex, interlocking letters' },
    { id: 'block', name: 'Block', description: 'Bold, square letters' },
    { id: 'tag', name: 'Tag', description: 'Quick, signature style' },
    { id: 'stencil', name: 'Stencil', description: 'Clean, cut-out style' },
  ];

  const generateGraffitiText = async () => {
    if (!text.trim()) {
      alert('Please enter some text to generate graffiti!');
      return;
    }

    // Moderate the text first
    const isAppropriate = await moderateText(text);
    if (!isAppropriate) {
      alert('Let\'s keep it creative and positive! Try something else 🎨');
      return;
    }

    setIsGenerating(true);

    try {
      // In a real implementation, this would call the Replicate API
      // For now, we'll create a text object with Fabric.js
      if (fabricCanvas) {
        const graffitiText = new fabric.Text(text, {
          left: fabricCanvas.width / 2 - 100,
          top: fabricCanvas.height / 2 - 25,
          fontFamily: getFontFamily(graffitiStyle),
          fontSize: fontSize,
          fill: textColor,
          stroke: '#000000',
          strokeWidth: 2,
          shadow: new fabric.Shadow({
            color: textColor,
            blur: 10,
            offsetX: 0,
            offsetY: 0,
          }),
        });

        fabricCanvas.add(graffitiText);
        fabricCanvas.setActiveObject(graffitiText);
        fabricCanvas.renderAll();
      }

      // Clear the input
      setText('');
      
    } catch (error) {
      console.error('Error generating graffiti text:', error);
      alert('Failed to generate graffiti text. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const getFontFamily = (style) => {
    const fontMap = {
      bubble: 'Boogaloo, cursive',
      wildstyle: 'Rubik Dirt, cursive',
      block: 'Permanent Marker, cursive',
      tag: 'Permanent Marker, cursive',
      stencil: 'monospace',
    };
    return fontMap[style] || 'Boogaloo, cursive';
  };

  return (
    <div className="toolbar p-4">
      <h3 className="text-lg font-bold mb-3 text-green-400">Text to Graffiti</h3>
      
      {/* Text Input */}
      <div className="mb-3">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter your text (max 40 chars)"
          className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-green-500 focus:outline-none"
          maxLength={40}
        />
        <p className="text-xs text-gray-400 mt-1">
          {text.length}/40 characters
        </p>
      </div>

      {/* Style Selection */}
      <div className="mb-3">
        <label className="block text-sm font-semibold mb-2 text-gray-300">
          Graffiti Style
        </label>
        <select
          value={graffitiStyle}
          onChange={(e) => setGraffitiStyle(e.target.value)}
          className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-green-500 focus:outline-none"
        >
          {graffitiStyles.map((style) => (
            <option key={style.id} value={style.id}>
              {style.name} - {style.description}
            </option>
          ))}
        </select>
      </div>

      {/* Font Size */}
      <div className="mb-3">
        <label className="block text-sm font-semibold mb-2 text-gray-300">
          Font Size: {fontSize}px
        </label>
        <input
          type="range"
          min="16"
          max="120"
          value={fontSize}
          onChange={(e) => setFontSize(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Text Color */}
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-2 text-gray-300">
          Text Color
        </label>
        <div className="flex items-center space-x-2">
          <input
            type="color"
            value={textColor}
            onChange={(e) => setTextColor(e.target.value)}
            className="w-12 h-8 rounded cursor-pointer"
          />
          <input
            type="text"
            value={textColor}
            onChange={(e) => setTextColor(e.target.value)}
            className="flex-1 p-1 text-xs bg-gray-800 border border-gray-700 rounded"
          />
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={generateGraffitiText}
        disabled={isGenerating || !text.trim()}
        className="toolbar-button w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isGenerating ? (
          <span className="flex items-center justify-center">
            <div className="loading-spinner w-4 h-4 mr-2"></div>
            Generating...
          </span>
        ) : (
          '🎨 Generate Graffiti Text'
        )}
      </button>

      <p className="text-xs text-gray-400 mt-2 text-center">
        AI-powered graffiti text generation
      </p>
    </div>
  );
};

export default TextToGraffiti;
