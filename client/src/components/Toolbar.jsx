import { useState } from 'react';

const Toolbar = ({ 
  selectedBrush, 
  setSelectedBrush, 
  clearCanvas, 
  downloadArtwork, 
  sendToDisplay, 
  isMobile = false 
}) => {
  const [showBrushMenu, setShowBrushMenu] = useState(false);

  const brushes = [
    { id: 'freehand', name: 'Brush', icon: '🖌️' },
    { id: 'spray', name: 'Spray', icon: '🎨' },
    { id: 'marker', name: 'Marker', icon: '🖊️' },
    { id: 'chalk', name: 'Chalk', icon: '📝' },
    { id: 'drip', name: 'Drip', icon: '💧' },
    { id: 'eraser', name: 'Eraser', icon: '🧹' },
  ];

  const layout = isMobile ? 'grid grid-cols-3' : 'flex flex-col space-y-2';

  return (
    <div className={`toolbar ${isMobile ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-bold mb-3 text-green-400 ${isMobile ? 'text-center' : ''}`}>
        Tools
      </h3>
      
      {/* Brush Selection */}
      <div className={`${layout} gap-2 mb-4`}>
        {brushes.map((brush) => (
          <button
            key={brush.id}
            onClick={() => setSelectedBrush(brush.id)}
            className={`toolbar-button ${selectedBrush === brush.id ? 'active' : ''} ${
              isMobile ? 'text-sm p-2' : ''
            }`}
            title={brush.name}
          >
            <span className={isMobile ? 'text-lg' : 'text-xl'}>{brush.icon}</span>
            {!isMobile && <span className="ml-2">{brush.name}</span>}
          </button>
        ))}
      </div>

      {/* Action Buttons */}
      <div className={`space-y-2 ${isMobile ? 'grid grid-cols-2 gap-2' : ''}`}>
        <button
          onClick={() => {
            // Undo functionality would be implemented here
            console.log('Undo action');
          }}
          className={`toolbar-button ${isMobile ? 'text-sm p-2' : ''}`}
        >
          ↩️ Undo
        </button>
        
        <button
          onClick={() => {
            // Redo functionality would be implemented here
            console.log('Redo action');
          }}
          className={`toolbar-button ${isMobile ? 'text-sm p-2' : ''}`}
        >
          ↪️ Redo
        </button>
        
        <button
          onClick={clearCanvas}
          className={`toolbar-button bg-red-600 hover:bg-red-700 ${
            isMobile ? 'text-sm p-2 col-span-2' : ''
          }`}
        >
          🗑️ Clear Canvas
        </button>
        
        <button
          onClick={downloadArtwork}
          className={`toolbar-button bg-blue-600 hover:bg-blue-700 ${
            isMobile ? 'text-sm p-2' : ''
          }`}
        >
          💾 Download
        </button>
        
        <button
          onClick={sendToDisplay}
          className={`toolbar-button bg-green-600 hover:bg-green-700 ${
            isMobile ? 'text-sm p-2' : ''
          }`}
        >
          📤 Send to Display
        </button>
      </div>
    </div>
  );
};

export default Toolbar;
