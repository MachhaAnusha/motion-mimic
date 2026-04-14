import { useState, useEffect, useRef } from 'react';
import { fabric } from 'fabric';
import Toolbar from '../components/Toolbar';
import ColorPicker from '../components/ColorPicker';
import BrushSelector from '../components/BrushSelector';
import TextToGraffiti from '../components/TextToGraffiti';
import TimerWidget from '../components/TimerWidget';
import { useCanvas } from '../hooks/useCanvas';
import { useSocket } from '../hooks/useSocket';
import { useModeration } from '../hooks/useModeration';

const CreatorView = () => {
  const canvasRef = useRef(null);
  const fabricCanvas = useRef(null);
  const [selectedColor, setSelectedColor] = useState('#39ff14');
  const [brushSize, setBrushSize] = useState(5);
  const [selectedBrush, setSelectedBrush] = useState('freehand');
  const [opacity, setOpacity] = useState(100);
  const [neonGlow, setNeonGlow] = useState(false);
  const [backgroundTexture, setBackgroundTexture] = useState('brick');
  const [nickname, setNickname] = useState('');
  const [showNicknameModal, setShowNicknameModal] = useState(true);
  const [isDrawing, setIsDrawing] = useState(false);
  const [timerDuration, setTimerDuration] = useState(180); // 3 minutes default

  const socket = useSocket();
  const { moderateText, moderateImage } = useModeration();

  // Initialize canvas
  useEffect(() => {
    if (canvasRef.current && !fabricCanvas.current) {
      // Calculate 16:9 aspect ratio canvas size
      const containerWidth = Math.min(window.innerWidth - 40, 1200);
      const canvasHeight = (containerWidth * 9) / 16;

      fabricCanvas.current = new fabric.Canvas(canvasRef.current, {
        width: containerWidth,
        height: canvasHeight,
        backgroundColor: '#1a1a1a',
        isDrawingMode: true,
      });

      // Set initial brush settings
      fabricCanvas.current.freeDrawingBrush.width = brushSize;
      fabricCanvas.current.freeDrawingBrush.color = selectedColor;

      // Handle window resize
      const handleResize = () => {
        const newWidth = Math.min(window.innerWidth - 40, 1200);
        const newHeight = (newWidth * 9) / 16;
        fabricCanvas.current.setDimensions({
          width: newWidth,
          height: newHeight,
        });
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (fabricCanvas.current) {
          fabricCanvas.current.dispose();
        }
      };
    }
  }, []);

  // Update brush settings when they change
  useEffect(() => {
    if (fabricCanvas.current && fabricCanvas.current.freeDrawingBrush) {
      fabricCanvas.current.freeDrawingBrush.width = brushSize;
      fabricCanvas.current.freeDrawingBrush.color = selectedColor;
      fabricCanvas.current.freeDrawingBrush.opacity = opacity / 100;
    }
  }, [selectedColor, brushSize, opacity]);

  // Handle drawing events
  useEffect(() => {
    if (fabricCanvas.current) {
      const handlePathCreated = (e) => {
        const path = e.path;
        if (neonGlow) {
          path.set({
            shadow: new fabric.Shadow({
              color: selectedColor,
              blur: 20,
              offsetX: 0,
              offsetY: 0,
            }),
          });
        }
        fabricCanvas.current.renderAll();
      };

      fabricCanvas.current.on('path:created', handlePathCreated);

      return () => {
        if (fabricCanvas.current) {
          fabricCanvas.current.off('path:created', handlePathCreated);
        }
      };
    }
  }, [selectedColor, neonGlow]);

  const clearCanvas = () => {
    if (fabricCanvas.current) {
      fabricCanvas.current.clear();
      fabricCanvas.current.backgroundColor = '#1a1a1a';
      fabricCanvas.current.renderAll();
    }
  };

  const downloadArtwork = () => {
    if (fabricCanvas.current) {
      const dataURL = fabricCanvas.current.toDataURL({
        format: 'png',
        quality: 1,
      });
      const link = document.createElement('a');
      link.download = `graffiti-${Date.now()}.png`;
      link.href = dataURL;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const sendToDisplay = async () => {
    if (!fabricCanvas.current) return;

    try {
      // Get canvas as base64
      const canvasData = fabricCanvas.current.toDataURL({
        format: 'png',
        quality: 0.8,
      });

      // Moderate the canvas content
      const isAppropriate = await moderateImage(canvasData);
      if (!isAppropriate) {
        alert('Let\'s keep it creative and positive! Try something else 🎨');
        return;
      }

      // Send to server
      const artworkData = {
        image: canvasData,
        nickname: nickname || 'Anonymous',
        timestamp: new Date().toISOString(),
      };

      socket?.emit('artwork:submit', artworkData);
      
      // Show success message
      alert('Your artwork has been sent to the display! 🎨');
      
    } catch (error) {
      console.error('Error sending artwork:', error);
      alert('Failed to send artwork. Please try again.');
    }
  };

  const handleBackgroundChange = (texture) => {
    setBackgroundTexture(texture);
    if (fabricCanvas.current) {
      const backgrounds = {
        brick: 'linear-gradient(45deg, #8B4513 25%, #A0522D 25%, #A0522D 50%, #8B4513 50%, #8B4513 75%, #A0522D 75%, #A0522D)',
        concrete: 'linear-gradient(45deg, #696969 25%, #808080 25%, #808080 50%, #696969 50%, #696969 75%, #808080 75%, #808080)',
        metal: 'linear-gradient(180deg, #C0C0C0 0%, #808080 50%, #C0C0C0 100%)',
        wood: 'linear-gradient(90deg, #8B4513 0%, #A0522D 25%, #8B4513 50%, #A0522D 75%, #8B4513 100%)',
        black: '#000000',
        white: '#FFFFFF',
      };

      fabricCanvas.current.setBackgroundColor(backgrounds[texture] || '#1a1a1a', () => {
        fabricCanvas.current.renderAll();
      });
    }
  };

  if (showNicknameModal) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div className="bg-gray-900 rounded-lg p-8 max-w-md w-full border-2 border-green-500">
          <h2 className="text-2xl font-bold text-green-400 mb-4 text-center font-graffiti">
            Welcome to AI Graffiti Wall!
          </h2>
          <p className="text-white mb-6 text-center">
            Enter your nickname (optional) to get started:
          </p>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="Enter your nickname"
            className="w-full p-3 rounded bg-gray-800 text-white border border-gray-700 focus:border-green-500 focus:outline-none"
            maxLength={20}
          />
          <button
            onClick={() => setShowNicknameModal(false)}
            className="w-full mt-4 bg-green-500 hover:bg-green-600 text-black font-bold py-3 px-6 rounded transition-colors"
          >
            Start Creating! 🎨
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-2 md:p-4">
      {/* Header */}
      <div className="text-center mb-4">
        <h1 className="text-3xl md:text-4xl font-bold text-green-400 font-graffiti neon-glow">
          AI Graffiti Wall
        </h1>
        <p className="text-gray-400 text-sm md:text-base">
          Create your digital masterpiece and share it with the world!
        </p>
      </div>

      {/* Timer Widget */}
      <TimerWidget 
        duration={timerDuration} 
        onTimeUp={sendToDisplay}
        isActive={true}
      />

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-4 max-w-7xl mx-auto">
        {/* Left Toolbar - Desktop */}
        <div className="hidden lg:block w-64 space-y-4">
          <Toolbar
            selectedBrush={selectedBrush}
            setSelectedBrush={setSelectedBrush}
            clearCanvas={clearCanvas}
            downloadArtwork={downloadArtwork}
            sendToDisplay={sendToDisplay}
          />
          
          <ColorPicker
            selectedColor={selectedColor}
            setSelectedColor={setSelectedColor}
            opacity={opacity}
            setOpacity={setOpacity}
            neonGlow={neonGlow}
            setNeonGlow={setNeonGlow}
          />
          
          <BrushSelector
            brushSize={brushSize}
            setBrushSize={setBrushSize}
          />
        </div>

        {/* Canvas Container */}
        <div className="flex-1 flex flex-col items-center">
          <div className="canvas-container w-full">
            <canvas
              ref={canvasRef}
              className="border-2 border-gray-700 rounded-lg"
            />
          </div>

          {/* Mobile Toolbar */}
          <div className="lg:hidden mt-4 w-full space-y-4">
            <Toolbar
              selectedBrush={selectedBrush}
              setSelectedBrush={setSelectedBrush}
              clearCanvas={clearCanvas}
              downloadArtwork={downloadArtwork}
              sendToDisplay={sendToDisplay}
              isMobile={true}
            />
            
            <ColorPicker
              selectedColor={selectedColor}
              setSelectedColor={setSelectedColor}
              opacity={opacity}
              setOpacity={setOpacity}
              neonGlow={neonGlow}
              setNeonGlow={setNeonGlow}
              isMobile={true}
            />
            
            <BrushSelector
              brushSize={brushSize}
              setBrushSize={setBrushSize}
              isMobile={true}
            />
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-full lg:w-80 space-y-4">
          {/* Background Options */}
          <div className="toolbar p-4">
            <h3 className="text-lg font-bold mb-3 text-green-400">Background</h3>
            <div className="grid grid-cols-2 gap-2">
              {['brick', 'concrete', 'metal', 'wood', 'black', 'white'].map((texture) => (
                <button
                  key={texture}
                  onClick={() => handleBackgroundChange(texture)}
                  className={`toolbar-button capitalize ${backgroundTexture === texture ? 'active' : ''}`}
                >
                  {texture}
                </button>
              ))}
            </div>
          </div>

          {/* Text to Graffiti */}
          <TextToGraffiti
            fabricCanvas={fabricCanvas.current}
            moderateText={moderateText}
          />

          {/* AI Enhancement */}
          <div className="toolbar p-4">
            <h3 className="text-lg font-bold mb-3 text-green-400">AI Enhancement</h3>
            <button className="toolbar-button w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              ✨ Enhance with AI
            </button>
            <p className="text-xs text-gray-400 mt-2">
              Transform your artwork with AI-powered style transfer
            </p>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="text-center mt-4 text-sm text-gray-500">
        Creating as: <span className="text-green-400 font-bold">{nickname || 'Anonymous'}</span>
      </div>
    </div>
  );
};

export default CreatorView;
